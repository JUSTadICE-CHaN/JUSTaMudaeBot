
import time
import datetime
import Config
import asyncio

class Timer:
    """
    Class to facilitate auto rolling on a timer.
    next_claim: datetime.datetime
        Time of next claim.
    next_roll: datetime.datetime
        Time of next roll.
    next_daily: datetime.datetime
        Time of next daily, or current time if it is ready.
    roll_count: int
        Number of times to roll.
    claim_available: bool
        Whether a claim is currently available or not.
    next_kakera: datetime.datetime
        Time of next kakera, or current time if it is ready.
    kakera_available: bool
        Whether a kakera loot is currently available or not.
    rolling_event: asyncio.Event
        Event to signal when rolling is done.
    """

    def __init__(self, next_claim, next_roll, next_daily, claim_available, next_kakera, kakera_available, channel, channel_id, client):
        self.claim_timer = next_claim
        self.roll_timer = next_roll
        self.daily_timer = next_daily
        self.claim_available = claim_available
        self.kakera_available = kakera_available
        self.kakera_timer = next_kakera
        self.claim_duration = Config.Claim
        self.roll_duration = Config.Roll
        self.daily_duration = Config.Daily
        self.channel = channel
        self.channel_id = channel_id
        self.client = client
        self.rolling_event = asyncio.Event()


    def get_claim_availability(self):
        return self.claim_available

    def set_claim_availability(self, available: bool):
        self.claim_available = available

    def get_kakera_availability(self):
        return self.kakera_available

    def set_kakera_availability(self, available: bool):
        self.kakera_available = available

    async def wait_for_roll(self):
        while True:
            x = (self.roll_timer - datetime.datetime.now()).total_seconds()
            print(f'Roll timer sleeping for {x:.0f} seconds for {self.channel.name}')
            await asyncio.sleep(x)
            self.roll_timer += datetime.timedelta(minutes=self.roll_duration)
            print(f'Rolls have been reset for {self.channel.name}')
            if Config.AlwaysRoll or self.claim_available:
                print(f'Initiating rolls for {self.channel.name}')
                await self.client.rolltest(self.channel_id)
            else:
                print(f'No claim available for {self.channel.name}, not rolling')

    async def wait_for_claim(self):
        while True:
            x = (self.claim_timer - datetime.datetime.now()).total_seconds()
            print(f'Claim timer sleeping for {x:.0f} seconds for {self.channel.name}')
            await asyncio.sleep(x)
            self.claim_timer += datetime.timedelta(minutes=self.claim_duration)
            print(f'Claims have been reset for {self.channel.name}')
            self.claim_available = True

    def is_last_min_claim_active(self) -> bool:
        """
        Checks if last_min_claim is active.
        Returns
        -------
        bool
            True if last_min_claim is active, False otherwise.
        """
        current_time = datetime.datetime.now()
        time_until_claim_reset = (self.claim_timer - current_time).total_seconds()
        if time_until_claim_reset <= 3600 and self.claim_available:
            return True
        return False

    async def wait_for_daily(self):
        while True:
            x = (self.daily_timer - datetime.datetime.now()).total_seconds()
            if x > 0:  # In case daily is already ready
                print(f'Daily timer sleeping for {x:.0f} seconds for {self.channel.name}')
                await asyncio.sleep(x)
                print(f'Daily has been reset, initiating daily commands for {self.channel.name}')
            else:
                print(f'Daily is ready, initiating daily commands for {self.channel.name}')
            self.daily_timer += datetime.timedelta(minutes=self.daily_duration)
            main_channel = self.channel_id
            sub_channels = Config.Channels.get(main_channel, [])

            # Send message $dk in all main channels
            await self.send_messages([main_channel] + sub_channels, '$dk')
            await asyncio.sleep(3)  # Wait 3 seconds for processing

            # Send message $daily only in the first main channel
            if main_channel == list(Config.Channels.keys())[0]:
                await self.client.get_channel(main_channel).send('$daily')

    async def wait_for_p(self):
        while True:
            await asyncio.sleep(3 * 60 * 60)  # Wait for 3 hours
            main_channel = self.channel_id
            sub_channels = Config.Channels.get(main_channel, [])

            # Send message $p only in the first main channel
            if main_channel == list(Config.Channels.keys())[0]:
                await self.send_messages([main_channel], '$p')

    async def send_messages(self, channels, message):
        main_channels = [channel_id for channel_id in channels if channel_id in Config.Channels]
        for channel_id in main_channels:
            await self.client.get_channel(channel_id).send(message)

    def get_timers(self):
        """
        Get the current timers.
        Returns
        -------
        dict
            A dictionary containing the current timers.
        """
        current_time = datetime.datetime.now()
        return {
            'claim_timer': (self.claim_timer - current_time).total_seconds(),
            'roll_timer': (self.roll_timer - current_time).total_seconds(),
            'daily_timer': (self.daily_timer - current_time).total_seconds(),
            'kakera_timer': (self.kakera_timer - current_time).total_seconds()
        }
