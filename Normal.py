import discum
import discord
import Config
import threading
import asyncio
import time
import datetime
import re
from MudaeSchedule import Timer
from EzMudae import Mudae
from discum.utils.slash import SlashCommander

bot_id = 432610292342587392
botID = '432610292342587392'
bot = discum.Client(token=Config.Token, log=False)
rollCommand = SlashCommander(bot.getSlashCommands(botID).json()).get([Config.Rollcommand])
reaction_lock = asyncio.Lock()

class MyClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.allowed_guilds = Config.Servers
        self.rolling = {}
        self.is_ready = False

    async def on_ready(self):
        if self.is_ready:
            return
        print(f'Logged on as {self.user.name} ({self.user.id})')
        await self.initialize_channels()

    async def initialize_channels(self):
        channel_status = {channel_id: False for channel_id in Config.Channels.keys()}

        while not all(channel_status.values()):
            for main_channel, sub_channels in Config.Channels.items():
                if channel_status[main_channel]:
                    continue

                await self.process_channel(main_channel, channel_status)

        self.is_ready = True
        print("All channels processed. Ready.")

    async def process_channel(self, main_channel, channel_status):
        await asyncio.sleep(1)
        main_channel_obj = self.get_channel(main_channel)

        try:
            print(f'Sending message in {main_channel_obj.name}')
            await main_channel_obj.send(Config.Rollprefix + 'tu')
            message = await self.wait_for('message', timeout=3, check=lambda m: m.channel == main_channel_obj)
            await asyncio.sleep(1)
            await self.tuparsing(message, main_channel)
            channel_status[main_channel] = True
            await self.print_current_timers(main_channel_obj, main_channel, message)

        except asyncio.TimeoutError:
            print(f'No response received in {main_channel_obj.name} within 3 seconds')
            self.handle_timeout(main_channel_obj, message, main_channel, channel_status)

    async def print_current_timers(self, main_channel_obj, main_channel, message):
        try:
            timers = self.rolling[main_channel].get_timers()
            print(f"Current timers for {main_channel_obj.name}: {timers}")
        except:
            await self.find_previous_message(main_channel_obj, main_channel, message)

    def handle_timeout(self, main_channel_obj, message, main_channel, channel_status):
        self.find_previous_message(main_channel_obj, main_channel)
        try:
            timers = self.rolling[main_channel].get_timers()
            print(f"Current timers for {main_channel_obj.name}: {timers}")
        except:
            self.find_previous_message(main_channel_obj, main_channel, message)
        channel_status[main_channel] = True

    async def find_previous_message(self, main_channel_obj, main_channel, message):
        user_message = None
        async for prev_message in main_channel_obj.history(limit=10, before=message):
            if prev_message.author.id == self.user.id and f'{Config.Rollprefix}tu' in prev_message.content:
                user_message = prev_message
                break
        if user_message:
            async for prev_message in main_channel_obj.history(limit=10, after=user_message):
                if str(bot_id) in prev_message.content and self.user.name in prev_message.content:
                    print(f'Found previous message containing bot ID and user ID in {main_channel_obj.name}')
                    await self.tuparsing(prev_message, main_channel)
                    timers = self.rolling[main_channel].get_timers()
                    print(f"Current timers for {main_channel_obj.name}: {timers}")
                    break
        else:
            print(f'No relevant previous message found in {main_channel_obj.name}')

    async def tuparsing(self, message, main_channel):
        if message.author == self.user:
            return

        match = re.search(r"""^.*?\*\*(.*?)\*\*.*?                          # Group 1: Username
                                (can't|can).*?                              # Group 2: Claim available
                                (\d+(?:h\ \d+)?)(?=\*\*\ min).*?            # Group 3: Claim reset
                                (\d+(?:h\ \d+)?)(?=\*\*\ min).*?            # Group 4: Rolls reset
                                (?<=\$daily).*?(available|\d+h\ \d+).*?     # Group 5: $daily reset
                                (can't|can).*?(?=react).*?                  # Group 6: Kakera available
                                (?:(\d+(?:h\ \d+)?)(?=\*\*\ min)|(now)).*?  # Group 7: Kakera reset
                                (?<=\$dk).*?(ready|\d+h\ \d+)               # Group 8: $dk reset
                                .*$                                         # End of string
                                """, message.content, re.DOTALL | re.VERBOSE)
        if not match or match.group(1) != self.user.name:
            return

        times = [self.parse_time(match.group(i)) for i in [3, 4, 5, 7]]
        kakera_available = match.group(6) == 'can'
        claim_available = match.group(2) == 'can'

        timing_info = {
            'claim_reset': datetime.datetime.now() + datetime.timedelta(minutes=times[0]),
            'claim_available': claim_available,
            'rolls_reset': datetime.datetime.now() + datetime.timedelta(minutes=times[1], seconds=30),
            'kakera_available': kakera_available,
            'kakera_reset': datetime.datetime.now() + datetime.timedelta(minutes=times[3]),
            'daily_reset': datetime.datetime.now() + datetime.timedelta(minutes=times[2]),
        }

        sub_channels = Config.Channels[main_channel]
        self.update_timers(timing_info, main_channel, sub_channels)

    def parse_time(self, time_str):
        if time_str is None:
            return 0
        elif 'h ' in time_str:
            hours, minutes = map(int, time_str.split('h '))
            return hours * 60 + minutes
        elif time_str in {'ready', 'now', 'available'}:
            return 0
        else:
            return int(time_str)

    def update_timers(self, timing_info, main_channel, sub_channels):
        for channel_id in [main_channel] + sub_channels:
            self.rolling[channel_id] = Timer(
                timing_info["claim_reset"],
                timing_info["rolls_reset"],
                timing_info["daily_reset"],
                timing_info['claim_available'],
                timing_info["kakera_reset"],
                timing_info["kakera_available"],
                self.get_channel(channel_id),
                channel_id,
                self
            )

            if channel_id == main_channel:
                asyncio.create_task(self.rolling[channel_id].wait_for_p())
                asyncio.create_task(self.rolling[channel_id].wait_for_claim())
                if Config.Daily > 0:
                    asyncio.create_task(self.rolling[channel_id].wait_for_daily())
                if Config.Roll > 0:
                    asyncio.create_task(self.rolling[channel_id].wait_for_roll())

    async def on_message(self, message):
        if not self.is_ready:
            return

        if self.is_valid_message(message):
            return

        mudae_wrap = Mudae(self, None)

        waifu = mudae_wrap.waifu_from(message)

        main_channel_id = self.get_main_channel_id(message.channel.id)
        if not main_channel_id:
            return

        if waifu:
            await self.handle_waifu_message(waifu, message, main_channel_id)
        else:
            await self.handle_bot_message(message)

    def is_valid_message(self, message):
        return (
            message.author == self.user or
            message.guild is None or
            message.guild.id not in self.allowed_guilds or
            (
                message.channel.id not in Config.Channels and 
                not any(message.channel.id in subchannels for subchannels in Config.Channels.values())
            )
        )


    def get_main_channel_id(self, channel_id):
        for main_channel, sub_channels in Config.Channels.items():
            if channel_id == main_channel or channel_id in sub_channels:
                return main_channel
        return None

    async def handle_waifu_message(self, waifu, message, main_channel_id):
        embed = message.embeds[0]
        waifu_dict = {attr: getattr(waifu, attr) for attr in dir(waifu) if not attr.startswith('__') and not callable(getattr(waifu, attr))}

        if waifu.type == waifu.Type.info:
            print("Just an $im command or something")
        elif embed.thumbnail:
            print("probably mm")
        else:
            await self.process_waifu_claim(waifu, message, main_channel_id)

    async def process_waifu_claim(self, waifu, message, main_channel_id):
        channel_name = f"{message.channel.name} ({message.guild})" if isinstance(message.channel, discord.TextChannel) else "Unknown"
        user = message.author.name if message.interaction is None else message.interaction.user.name

        if message.interaction is None:
            async for prev_message in message.channel.history(limit=5, before=message):
                if Config.Rollprefix in prev_message.content:
                    user = prev_message.author.name
                    break

        if waifu.is_claimed:
            print(f"❤️ ---- {waifu.kakera} - {waifu} - {waifu.series} - in {channel_name} by {user}")
            if ((user != self.user.name) and Config.SnipeKak) or user == self.user.name:
                await self.attempt_kakera_snipe(message, waifu)
        else:
            print(f"🤍 ---- {waifu.kakera} - {waifu} - {waifu.series} - in {channel_name} by {user}")
            if ((user != self.user.name) and Config.Snipe) or user == self.user.name:
                await self.attempt_claim(waifu, message, main_channel_id)

    async def attempt_kakera_snipe(self, message, waifu):
        if message.components:
            for child in message.components[0].children:
                if child.emoji.name.lower() in [k.lower() for k in Config.Kakera]:
                    print(f"{child.emoji.name} for {waifu} will not be claimed as its been disabled")
                    pass
                else:
                    print(f"\nAttempting to snipe kakera for {waifu} ({child.emoji.name})\n")
                    await child.click()
                
    async def attempt_claim(self, waifu, message, main_channel_id):
        if waifu.kakera > Config.lastminkak or waifu.kakera > Config.minkak or waifu.name in Config.Wishlist:
            if self.rolling[main_channel_id].get_claim_availability():
                if self.rolling[main_channel_id].is_last_min_claim_active():
                        if waifu.kakera >= Config.lastminkak or waifu.name in Config.Wishlist:
                            await self.claim_waifu(message, waifu)
                elif waifu.kakera >= Config.minkak or waifu.name in Config.Wishlist:
                    await self.claim_waifu(message, waifu)
            else:
                print(f"No Claim Available for - {message.channel.name} - to claim {waifu}")

    async def claim_waifu(self, message, waifu):
        print(f"\nTrying to claim {waifu}\n")
        if message.components:
            print("Possibly a wish")
            for child in message.components[0].children:
                await child.click()
            await message.add_reaction('❤️')
        else:
            await message.add_reaction('❤️')

    async def handle_bot_message(self, message):
        if message.author.id == bot_id:
            if 'Upvote Mudae to reset the timer:' in message.content and f'**{self.user.name}**' in message.content:
                channel_id = message.channel.id
                self.rolling[channel_id].rolling_event.set()

    async def on_reaction_add(self, reaction, user):
        async with reaction_lock:
            if user != self.user:
                return

            message = reaction.message

            if self.is_valid_message(message):
                return

            main_channel_id = self.get_main_channel_id(message.channel.id)
            if not main_channel_id:
                return

            await self.process_reaction(reaction, message, main_channel_id)

    async def process_reaction(self, reaction, message, main_channel_id):
        mudae_wrap = Mudae(self, None)
        waifu = mudae_wrap.waifu_from(message)
        await asyncio.sleep(2)
        async for next_message in reaction.message.channel.history(limit=20, after=message):
            if next_message.author.id == bot_id and self.user.name in next_message.content and waifu.name in next_message.content:
                await reaction.message.channel.send('ezez')
                print(f"{waifu.name} Claimed")
                self.rolling[main_channel_id].set_claim_availability(False)
                if not Config.AlwaysRoll:
                    self.rolling[main_channel_id].rolling_event.set()
                break
            elif f"<@{self.user.id}>" in next_message.content and "For this server" in message.content:
                self.rolling[main_channel_id].set_claim_availability(False)
                print("Claim already used")
                if not Config.AlwaysRoll:
                    self.rolling[main_channel_id].rolling_event.set()
                break

    async def rolltest(self, channel_id):
        channel = self.get_channel(channel_id)
        print(f"\nRolling is beginning for {channel.name} at {datetime.datetime.now().strftime('%H:%M:%S')}")

        main_channel_id = self.get_main_channel_id(channel_id)
        if not main_channel_id:
            return

        self.rolling[channel_id].rolling_event = threading.Event()

        while not self.rolling[channel_id].rolling_event.is_set():
            bot.triggerSlashCommand(bot_id, str(channel_id), str((self.get_channel(main_channel_id)).guild.id), data=rollCommand)
            await asyncio.sleep(1.8)

        print(f"Rolling has ended for {channel.name} at {datetime.datetime.now().strftime('%H:%M:%S')}")
        self.rolling[channel_id].rolling = False

client = MyClient()
client.run(Config.Token)
