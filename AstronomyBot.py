import discord
import bs4
import requests
import datetime
import mwapi
import wikipediaapi
import asyncio
import random

from discord.ext import commands
from bs4 import BeautifulSoup

class AstronomyBot(commands.Bot):
    def __init__(self, command_prefix="$", intents=None):
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        self.NASA_API = "{}" #NASA API
        self.NEWS_API = "{}" #news API
        self.CELESTIAL_BODIES = [] #randomization
        self.random_objects_settings = {}

        self.setup_commands()

    def setup_commands(self):
        self.add_command(self.locate_random)
        self.add_command(self.locate_celestial_object)
        self.add_command(self.set)
        self.add_command(self.send_random_objects)
        self.add_command(self.locate)
        self.add_command(self.news)
        self.add_command(self.photo)
        self.add_command(self.asteroids)
        self.add_command(self.astronomy_help)

    def collect_asteroids(self, start, end):
        response = requests.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start}&end_date={end}&api_key={self.NASA_API}")

        if response.status_code == 200:
            data = response.json()['near_earth_objects']

        return data

    async def locate_random(self, ctx):
        try:
            celestial_object = random.choice(self.CELESTIAL_BODIES)
            await self.locate_celestial_object(ctx, celestial_object)

        except Exception as e:
            await ctx.send(f"> Could not retrieve Astronomical Data. Error: {e}")


    async def locate_celestial_object(self, ctx, celestial_object):
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
                        # Add more conditions for additional fields as needed
                        if "Epoch" in header.text or "Equinox" in header.text:
                            embed.add_field(name=f"`Stellar Position:` {data.text}", value="", inline=False)
                        
                        elif "Constellation" in header.text:
                            embed.add_field(name=f"`Constellation:` {data.text}", value="", inline=False)

            if image_url:
                embed.set_image(url=image_url)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"> Could not retrieve Astronomical Data. Error: {e}")


    async def set(self, ctx, channel: discord.TextChannel, time: int):
        try:
            if time <= 0:
                await ctx.send("> Please enter a valid time interval (greater than 0).")
                return

            self.random_objects_settings[channel.id] = time
            await ctx.send(f"> Random astronomy objects will be sent to {channel.mention} every {time} hour(s), starting now.")

            self.loop.create_task(self.send_random_objects(channel, time))

        except Exception as e:
            await ctx.send(f"> Failed to set random astronomy objects. Error: {e}")


    async def send_random_objects(self, channel, time):
        try:
            while True:
                celestial_object = random.choice(self.CELESTIAL_BODIES)
                await self.locate_celestial_object(channel, celestial_object)
                await asyncio.sleep(time * 3600)

        except Exception as e:
            print(f"Error in sending random objects: {e}")


    async def locate(self, ctx, *, celestial_object):
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
                        # Add more conditions for additional fields as needed
                        if "Epoch" in header.text or "Equinox" in header.text:
                            embed.add_field(name=f"`Stellar Position:` {data.text}", value="", inline=False)
                        
                        elif "Constellation" in header.text:
                            embed.add_field(name=f"`Constellation:` {data.text}", value="", inline=False)

            if image_url:
                embed.set_image(url=image_url)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"> Could not retrieve Astronomical Data. Error: {e}")


    async def news(self, ctx, when='today'):
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


    async def photo(self, ctx, *, date: str = ""):
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


    async def asteroids(self, ctx, *, date: str = ""):
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


    async def astronomy_help(self, ctx):
        embed = discord.Embed(title="Astronomer | Bot Commands", color=discord.Color.blue())

        embed.add_field(name="", value="\n", inline=False)
        embed.add_field(name="`Celestial Body Search`", value="", inline=False)
        embed.add_field(name="", value="\n", inline=False)

        embed.add_field(name="$locate [object], $locate_random", value="Recieve relevant information about any celestial body.", inline=False)
        embed.add_field(name="", value="Be advised that the identifier must be an astronomical object. Example usage includes '$locate Antares' or '$locate Milky Way'. Keep in mind that sometimes you may have to put additional identifiers. For example, '$locate Andromeda' does not work, but '$locate Andromeda Galaxy' will.", inline=False)

        embed.add_field(name="", value="\n", inline=False)
        embed.add_field(name="`Photo of the Day (NASA)`", value="", inline=False)
        embed.add_field(name="", value="\n", inline=False)

        embed.add_field(name="$photo today", value="Get NASAs photo of the day.", inline=False)
        embed.add_field(name="$photo yesterday", value="Get NASAs photo of the day, from yesterday.", inline=False)
        embed.add_field(name="$photo YYYY-MM-DD", value="Get NASAs photo of the day, from a specific date.", inline=False)

        embed.add_field(name="", value="\n", inline=False)
        embed.add_field(name="`Astronomical News`", value="", inline=False)
        embed.add_field(name="", value="\n", inline=False)

        embed.add_field(name="$news today, $news tomorrow", value="Get space news/events for today.", inline=False)
        embed.add_field(name="", value="Keep in mind that this function will only display 3 new sources from the top headlines.", inline=False)

        embed.add_field(name="", value="\n", inline=False)
        embed.add_field(name="`Extras:`", value="", inline=False)
        embed.add_field(name="", value="\n", inline=False)

        embed.add_field(name="$asteroids today", value="Closest asteroids to earth today.", inline=False)
        embed.add_field(name="", value="Keep in mind that this function will only display 3 random earth-passing objects, otherwise the data would overload the embed limit.", inline=False)
        embed.add_field(name="$set {channel} {time;in hours}", value="Have the bot send random astronomical objects every interval of time you put (in hours)", inline=False)
        embed.add_field(name="", value="Keep in mind that the bot must have the ability to send messages in the channel you wish to set it to.", inline=False)

        await ctx.send(embed=embed)


if __name__ == "__main__":
    bot = AstronomyBot()
    bot.run() #my classified token
