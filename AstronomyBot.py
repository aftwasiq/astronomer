import discord
from discord.ext import commands
import bs4
from bs4 import BeautifulSoup

import requests
import datetime
import mwapi
import wikipediaapi
import asyncio
import random

#I have this list of Celestial Bodies for randomization as some objects dont fullfill all the list of attributes, so instead of searching for random one on wikipedia, it'll get a random one from here than get it's info. When a user does $locate_random, I don't want them to find an object that only has some attributes. Of course, I still have to troubleshoot further in order to make sure every object flawlessly showcases every single attribute, until then I'll just keep adding objects I think are cool (and fullfill the object requirements) to this list.

CELESTIAL_BODIES = [
    "Antares", "Proxima Centauri", "Betelgeuse", "Aldebaran", "Altair",
    "Andromeda Galaxy", "Pinwheel Galaxy", "Black Eye Galaxy", "Messier 81",
    "Cygnus X-1", "TON 618", "Sagittarius A*"
]

random_objects_settings = {}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

#News and NASA APIS
NASA_API = "{}"
NEWS_API = "{}"

def collect_asteroids(start, end):
    response = requests.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start}&end_date={end}&api_key={NASA_API}")
    
    if response.status_code == 200:
        data = response.json()['near_earth_objects']
    
    return data

@bot.command()
async def locate_random(ctx):
    try:
        celestial_object = random.choice(CELESTIAL_BODIES)
        await locate_celestial_object(ctx, celestial_object)

    except Exception as e:
        await ctx.send(f"> Could not retrieve Astronomical Data. Error: {e}")

async def locate_celestial_object(ctx, celestial_object):
    try:
        session = mwapi.Session("https://en.wikipedia.org/", user_agent="AstronomyBot/1.0")

        response = session.get(action="parse", page=celestial_object, prop="text", format="json")
        html = response["parse"]["text"]["*"]

        astronomical_terms = ["supernova", "nebula", "stellar", "planet",
                              "galactic", "interstellar", "cosmic", "exoplanet"
                             "galaxy", "binary star", "constellation", "light years"]

        if not any(term in html.lower() for term in astronomical_terms):
            await ctx.send(f"> {celestial_object} does not appear to be an astronomical object. Push **$astronomy_help** if you are having issues.")
            return

        soup = BeautifulSoup(html, "html.parser")
        image_element = soup.find("img")
        image_url = "https:" + image_element["src"] if image_element else None

        response = session.get(action="query", prop="extracts", titles=celestial_object, format="json", exintro=True, explaintext=True)
        page_data = list(response["query"]["pages"].values())[0]
        summary = page_data.get("extract", "No information available.")

        sentences = '. '.join(summary.split('.')[:5])

        embed = discord.Embed(title=f"{celestial_object.upper()}", description=sentences, color=discord.Color.blue())

        info_table = soup.find("table", {"class": "infobox"})

        if info_table:
            rows = info_table.find_all("tr")

            for row in rows:
                header = row.find("th")
                data = row.find("td")

                if header and data:
                    if "Epoch" in header.text or "Equinox" in header.text:
                        embed.add_field(name=f"`Stellar Position:` {data.text}", value="", inline=False)
                    
                    elif "Constellation" in header.text:
                        embed.add_field(name=f"`Constellation:` {data.text}", value="", inline=False)
                        
                    elif "Distance" in header.text and ("Earth" in header.text or "Sun" in header.text):
                        embed.add_field(name=f"`Distance from Earth:` {data.text}", value = "", inline=False)
                        
                    elif "Evolutionary" in header.text:
                        embed.add_field(name=f"`Evolutionary Stage:` {data.text}", value = "", inline=False)
                        
                    elif "Redshift" in header.text:
                        embed.add_field(name=f"`Redshift:` {data.text}", value = "", inline=False)
                        
                    elif "Luminosity" in header.text:
                        embed.add_field(name=f"`Luminosity:` {data.text}", value = "", inline=False)
                        
                    elif "Temperature" in header.text:
                        embed.add_field(name=f"`Temperature:` {data.text}", value = "", inline=False)
                        
                    elif "Discovery date" in header.text:
                        embed.add_field(name=f"`Discovery date:` {data.text}", value = "", inline=False)
                        
                    elif "Star" in header.text:
                        embed.add_field(name=f"`Orbiting Star:` {data.text}", value = "", inline=False)
                        
                    elif "Inclination" in header.text:
                        embed.add_field(name=f"`Inclination:` {data.text}", value = "", inline=False)
                        
                    elif "Surface gravity" in header.text:
                        embed.add_field(name=f"`Surface gravity:` {data.text}", value = "", inline=False)
                        
                    elif "Right ascension" in header.text:
                        embed.add_field(name=f"`Right Ascension:` {data.text}", value = "", inline=False) 
                        
                    elif "Declination" in header.text:
                        embed.add_field(name=f"`Declination:` {data.text}", value = "", inline=False) 


        if image_url:
            embed.set_image(url=image_url)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"> Could not retrieve Astronomical Data. Error: {e}")

@bot.command()
async def set(ctx, channel: discord.TextChannel, time: int):
    try:
        if time <= 0:
            await ctx.send("> Please enter a valid time interval (greater than 0).")
            return

        random_objects_settings[channel.id] = time
        await ctx.send(f"> Random astronomy objects will be sent to {channel.mention} every {time} hour(s), starting now.")

        bot.loop.create_task(send_random_objects(channel, time))

    except Exception as e:
        await ctx.send(f"> Failed to set random astronomy objects. Error: {e}")

async def send_random_objects(channel, time):
    try:
        while True:
            celestial_object = random.choice(CELESTIAL_BODIES)
            await locate_celestial_object(channel, celestial_object)
            await asyncio.sleep(time * 3600)  

    except Exception as e:
        print(f"Error in sending random objects: {e}")

@bot.command()
async def locate(ctx, *, celestial_object):
    try:
        session = mwapi.Session("https://en.wikipedia.org/", user_agent="AstronomyBot/1.0")

        response = session.get(action="parse", page=celestial_object, prop="text", format="json")
        html = response["parse"]["text"]["*"]

        astronomical_terms = ["supernova", "nebula", "stellar", "planet",
                              "galactic", "interstellar", "cosmic", "exoplanet"
                             "galaxy", "binary star", "constellation", "light years"]

        if not any(term in html.lower() for term in astronomical_terms):
            await ctx.send(f"> {celestial_object} does not appear to be an astronomical object. Push **$astronomy_help** if you are having issues.")
            return

        soup = BeautifulSoup(html, "html.parser")
        image_element = soup.find("img")
        image_url = "https:" + image_element["src"] if image_element else None

        response = session.get(action="query", prop="extracts", titles=celestial_object, format="json", exintro=True, explaintext=True)
        page_data = list(response["query"]["pages"].values())[0]
        summary = page_data.get("extract", "No information available.")

        sentences = '. '.join(summary.split('.')[:5])

        embed = discord.Embed(title=f"{celestial_object.upper()}", description=sentences, color=discord.Color.blue())

        info_table = soup.find("table", {"class": "infobox"})

        if info_table:
            rows = info_table.find_all("tr")

            for row in rows:
                header = row.find("th")
                data = row.find("td")

                if header and data:
                    if "Epoch" in header.text or "Equinox" in header.text:
                        embed.add_field(name=f"`Stellar Position:` {data.text}", value="", inline=False)
                    
                    elif "Constellation" in header.text:
                        embed.add_field(name=f"`Constellation:` {data.text}", value="", inline=False)
                        
                    elif "Distance" in header.text and ("Earth" in header.text or "Sun" in header.text):
                        embed.add_field(name=f"`Distance from Earth:` {data.text}", value = "", inline=False)
                        
                    elif "Evolutionary" in header.text:
                        embed.add_field(name=f"`Evolutionary Stage:` {data.text}", value = "", inline=False)
                        
                    elif "Redshift" in header.text:
                        embed.add_field(name=f"`Redshift:` {data.text}", value = "", inline=False)
                        
                    elif "Luminosity" in header.text:
                        embed.add_field(name=f"`Luminosity:` {data.text}", value = "", inline=False)
                        
                    elif "Temperature" in header.text:
                        embed.add_field(name=f"`Temperature:` {data.text}", value = "", inline=False)
                        
                    elif "Discovery date" in header.text:
                        embed.add_field(name=f"`Discovery date:` {data.text}", value = "", inline=False)
                        
                    elif "Star" in header.text:
                        embed.add_field(name=f"`Orbiting Star:` {data.text}", value = "", inline=False)
                        
                    elif "Inclination" in header.text:
                        embed.add_field(name=f"`Inclination:` {data.text}", value = "", inline=False)
                        
                    elif "Surface gravity" in header.text:
                        embed.add_field(name=f"`Surface gravity:` {data.text}", value = "", inline=False)
                        
                    elif "Right ascension" in header.text:
                        embed.add_field(name=f"`Right Ascension:` {data.text}", value = "", inline=False) 
                        
                    elif "Declination" in header.text:
                        embed.add_field(name=f"`Declination:` {data.text}", value = "", inline=False) 


        if image_url:
            embed.set_image(url=image_url)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"> Could not retrieve Astronomical Data. Perhaps you mispelt your inquiry?")



@bot.command()
async def news(ctx, when='today'):
    try:
        if when == 'today':
            date = datetime.date.today().isoformat()
        elif when == 'yesterday':
            date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        else:
            await ctx.send('> Invalid usage, only today and yesterday. **$astronomy_help** for assistance.')
            return

        news_url = f'https://newsapi.org/v2/top-headlines'
        params = {
            'q': 'space',
            'category': 'science',
            'apiKey': NEWS_API,
            'pageSize': 10, 
            'from': date,
            'to': date
        }
        response = requests.get(news_url, params=params)
        response.raise_for_status()  

        news_data = response.json()

        articles_with_images = [article for article in news_data['articles'] if article.get('urlToImage')]
        articles_to_display = articles_with_images[:3]

        embed = discord.Embed(title=f'Space News ({when.capitalize()})', color=discord.Color.blue())

        for article in articles_to_display:
            title = article['title']
            link = article['url']
            img_url = article['urlToImage']

            embed.add_field(name=title, value=f'[Read Article]({link})', inline=False)
            embed.set_image(url=img_url)

        await ctx.send(embed=embed)

    except requests.RequestException as e:
        await ctx.send(f'Failed to fetch space news. Error: {e}')


@bot.command()
async def photo(ctx, *, date: str = ""):
    if date == "today":
        date = datetime.date.today().isoformat()
        
    elif date == "yesterday":
        date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        
    else:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await ctx.send(
                "> Invalid format. Use **$photo today**, **yesterday**, or **YYYY-MM-DD**. \n> Use **$astronomy_help** for more info.")
            return

    response = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API}&date={date}")
    data = response.json()

    embed = discord.Embed(
        title = data["title"],
        description = data["explanation"],
        color = discord.Color.blue()
    )
    embed.set_image(url = data["url"])
    await ctx.send(embed = embed)
    
@bot.command()
async def asteroids(ctx, *, date: str = ""):
    if date == "today":
        date = datetime.date.today().isoformat()
        end_date = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
        
    elif date == "tomorrow":
        date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        end_date = (datetime.date.today() + datetime.timedelta(days=8)).isoformat()
       
    else:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await ctx.send(
                "> Invalid format. Use **$photo today**, **yesterday**, or **YYYY-MM-DD**. \n> Use **$astronomy help** for more info.")
            return
        
    asteroid_data = collect_asteroids(date, end_date)
    
    embed = discord.Embed(title=f"Asteroids/Earth-Passing Objects today: ", color=discord.Color.blue())
        
    for asteroid in list(asteroid_data.values())[:3]:
        name = asteroid[0]["name"]
        diameter = asteroid[0]["estimated_diameter"]["kilometers"]["estimated_diameter_max"]
        distance = asteroid[0]["close_approach_data"][0]["miss_distance"]["kilometers"]
        orbiting_body = asteroid[0]["close_approach_data"][0]["orbiting_body"]

        embed.add_field(name="", value = "", inline=False)
        embed.add_field(name=f"`Object {name}`", value = "", inline=False)
        embed.add_field(name="", value = "", inline=False)
        
        embed.add_field(name="Diameter (km)", value = diameter, inline=False)
        embed.add_field(name="Closest Approach Distance (km)", value = distance, inline=False)
        embed.add_field(name="Orbiting Body", value = orbiting_body, inline=False)
    
    await ctx.send(embed=embed)
    
@bot.command()
async def astronomy_help(ctx):
    embed = discord.Embed(title="Astronomer | Bot Commands", color=discord.Color.blue())
    
    embed.add_field(name="", value="\n", inline=False)
    embed.add_field(name= "`Celestial Body Search`", value= "", inline=False)
    embed.add_field(name="", value="\n", inline=False)

    embed.add_field(name= "$locate [object], $locate_random", value= "Recieve relevant information about any celestial body.", inline=False)
    embed.add_field(name= "", value= "Be advised that the identifier must be an astronomical object. Example usage includes '$locate Antares' or '$locate Milky Way'. Keep in mind that sometimes you may have to put additional identifiers. For example, '$locate Andromeda' does not work, but '$locate Andromeda Galaxy' will.", inline=False)
    
    embed.add_field(name="", value="\n", inline=False)
    embed.add_field(name= "`Photo of the Day (NASA)`", value= "", inline=False)
    embed.add_field(name="", value="\n", inline=False)

    embed.add_field(name= "$photo today", value= "Get NASAs photo of the day.", inline=False)
    embed.add_field(name= "$photo yesterday", value= "Get NASAs photo of the day, from yesterday.", inline=False)
    embed.add_field(name= "$photo YYYY-MM-DD", value= "Get NASAs photo of the day, from a specific date.", inline=False)
    
    embed.add_field(name="", value="\n", inline=False)
    embed.add_field(name= "`Astronomical News`", value= "", inline=False)
    embed.add_field(name="", value="\n", inline=False)
    
    embed.add_field(name= "$news today, $news tomorrow", value= "Get space news/events for today.", inline=False)
    embed.add_field(name= "", value= "Keep in mind that this function will only display 3 new sources from the top headlines.", inline=False)
    
    embed.add_field(name="", value="\n", inline=False)
    embed.add_field(name= "`Extras:`", value= "", inline=False)
    embed.add_field(name="", value="\n", inline=False)
    
    embed.add_field(name= "$asteroids today", value= "Closest asteroids to earth today.", inline=False)
    embed.add_field(name= "", value= "Keep in mind that this function will only display 3 random earth-passing objects, otherwise the data would overload the embed limit.", inline=False)
    embed.add_field(name= "$set {channel} {time;in hours}", value= "Have the bot send random astronomical objects every interval of time you put (in hours)", inline=False)
    embed.add_field(name="", value="Keep in mind that the bot must have the ability to send messages in the channel you wish to set it to.", inline=False)
    
    await ctx.send(embed = embed)

bot.run(token)

