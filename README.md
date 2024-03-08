## Astronomer [v1.4]

Astronomer is a discord bot that allows you to peer into the skies and gain information on any celestial object; star, galaxy, or planet. You can also look at NASAs photo of the day, asteroids passing Earth, space-related news, and much more. You can add this bot to your discord server using this [link](https://discord.com/oauth2/authorize?client_id=1214283242887319592&permissions=27465313210048&scope=bot)

Push **$astronomy_help** on a discord chat that Astronomer has access to, in order to begin configuration or see a list of already-available commands to use. As of 2023/03/06, Astronomer is currently used in 10+ Discord Servers.

Astronomers features are limited at the moment, and many more are to come as I improve the bot further. This is the first (proper) Discord Bot I've made, which utilizes web-scraping, and integration of NASA Open APIs, Wikipedia Public APIs, and News APIs to fetch and display dynamic content related to celestial objects, space news, and astronomy. In all honesty, it may be a tad-bit messy, but I do plan on reworking several parts of it as time goes, depending on how popular the bot gets.

Astronomer currently runs 24/7 on a Heroku Server. I update the code sometimes and don't put all changes on github right away, so some of the code may be outdated in comparision to how the bot works right or if there are any code issues which I've probably removed or reworked and haven't updated here.

### What each file is used for:

`AstronomyBot.py`  |  Main python file which handles all the bots processes and how it works.
 
`Procfile`         |  Heroku procfile that specifies the commands to be executed for the app on startup. (in this case; bot).
 
`requirements.txt` |  A file containing all the packages and libraries required for application installation. 


Here are examples usages of current commands that Astronomer has: 

### `$locate {object}`, `$locate_random` 
Display information about any celestial object in the sky. 

![Screenshot 2024-03-06 211445](https://github.com/aftwasiq/discord.py-Astronomy-Bot/assets/97777254/4d1701ea-033b-4489-bfee-f6691b80896c)

### `$photo today`, `$photo yesterday`, `$photo YYYY-MM-DD`
Display NASAs APOD (Photo of the day) for today, yesterday, or another specified date.

![photo](https://github.com/aftwasiq/discord.py-Astronomy-Bot/assets/97777254/3d194afa-f05e-4ba5-8a41-d3352331900c)

### `$news today`, `$news yesterday`
Display space-related top headlines from today or yesterday. 

![news](https://github.com/aftwasiq/discord.py-Astronomy-Bot/assets/97777254/40750428-1939-4aa0-a4ef-657d40320e90)

### `$asteroids today` 
Display 3 random objects passing near earth today.

![Screenshot 2024-03-06 193035](https://github.com/aftwasiq/discord.py-Astronomy-Bot/assets/97777254/70224e3f-653d-4760-8237-db4951eeac9f)
