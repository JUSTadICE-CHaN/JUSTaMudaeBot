# JUSTaMudaeBot

This is a bot that utilizes some aspects of discord.py-self and discum to create a discord self bot that can claim wishes and characters above a min kakera, last minute claim and react to kakera. 

## Features
- Can claim characters above a certain kakera 
- Can last minute claim during the last 60 minutes of claim timer
- Can react to kakera buttons
- Can choose whether to snipe or not
- Can operate multiple servers and channels and have some channels share the same timers/properties
- Custom delay
- Selective Kakera Claim
- Custom claim message

## Installation

### Requirements

- Python 3.10+
- Being able to obtain discord token (You can use this [tool](https://chromewebstore.google.com/detail/discord-get-user-token/accgjfooejbpdchkfpngkjjdekkcbnfd))
- Being able to read
- Below are the module dependency installation commands
  - Simply copy paste them into command line (Terminal or windows powershell)

```pip install discord.py-self
pip install discum
pip install thread6
pip install datetime
pip install regex
pip install discord.py-self
pip install parse
```
## Using the bot

Fill in your details in Config, then go to a channel in one of the channels you want the bot to run in and call mudae help to get a help dm (either /help or $help or whatever your help command is). Then run normal.py, thats it. Please leave me a star if it works!

#### PLEASE MAKE SURE THAT YOUR $TU COMMAND LOOKS EXACTLY LIKE THIS
![image](https://github.com/user-attachments/assets/9793e3ba-b477-4e2d-bce2-9960cd63690b)
#### IF ITS NOT EXACTLY AS ABOVE YOU WILL HAVE PARSING ISSUES!!!
(i am working to make this less annoying)

## Credits

Credits to [Znunu’s EzMudae](https://github.com/Znunu/EzMudae) for the amazing module that allowed this project to even function in the first place and [JasonYuan869’s regex implementation](https://github.com/JasonYuan869/AutoWaifuClaimerV3).

## License

Released under MIT. See `LICENSE` for details.

## Disclaimer

I am not responsible for anything that goes wrong as a result of using this bot. This is a discord **selfbot** and may get you banned.
