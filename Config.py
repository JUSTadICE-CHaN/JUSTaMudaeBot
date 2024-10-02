Servers = [ 111111111111111, 22222222222,] #The actual server/guild ids
Channels = {
    1: [1.1, 1.2, 1.3], #The first one is the main channel, inside the brackets are the sub channels (channels within the same server) that have the same timers (roll resets, etc), The first channel is also where the daily vote and pokemon rolls will be done in
    2: [2.1, 2.2, 2.3],
}
Token = 'YOUR TOKEN HERE'
Rollcommand = 'ROLL COMMAND HERE (wa/wg/ma/etc)'
Rollprefix = 'YOUR ROLL PREFIX HERE (default is $)'

AlwaysRoll = True #Whether it continue to roll after a claim or not
Pokeroll = False # Whether you want to pokeroll or not i guess

Snipe = False #True to enable sniping others
SnipeKak = False #True to enable sniping others
Delay = 0 #Time for delaying claim
DelayKak = 0 #Time for delaying kakera
Message = 'ezez' #message you want to send when you claim a character, make it None to send nothing
# Example: Message = None (not sure if Message = '' will work let me know !!!)

Wishlist = ['Zero Two', 
            'Rem', 
            'Megumin',]

#Durations in minutes 
Daily = 1200
Claim = 180
Roll = 60

#Any Kakera in this List will be IGNORED AND NOT SNIPED, remove the ones you WANT TO CLAIM for the bot to claim them. 
Kakera = []
# All Known Kakera emojis
# 'KakeraP',
# 'Kakera',
# 'KakeraT',
# 'KakeraG',
# 'KakeraY',
# 'KakeraO',
# 'KakeraR',
# 'KakeraW',
# 'KakeraL',

#claim stuff
minkak = 200 #minimum kakera to claim
lastminkak = 50 #minimum kakera to claim in last 60 minutes before reset
