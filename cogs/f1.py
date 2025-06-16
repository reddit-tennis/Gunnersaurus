"""
Basic cog to show next F1 race
"""
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
import fastf1
import requests
from discord.ext import commands


class F1Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session_re = re.compile(r"Session(\d)(.*)")


    @commands.command()
    @commands.is_owner()
    async def f1sync(self, ctx) -> None:
        try:
            await ctx.bot.tree.sync()
            await ctx.send('Owner synced F1 command.')
        except Exception as e:
            await ctx.send(f'Failed to sync F1 command. Is the owner calling this?')

    @staticmethod
    def calculate_time_until(target_timestamp):
        now = datetime.now()
        delta = target_timestamp - now
        if delta.total_seconds() < 0:
            return "The next event has already started or finished!"
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'Next event starts in {days} days, {hours} hours, {minutes} minutes, {seconds} seconds!'            

    @commands.command(name="next", help="Show general info about the next F1 Race.")
    async def next_race_event(self, ctx):
        next_race = requests.get("https://api.jolpi.ca/ergast/f1/current/next.json").json()
        next_round = next_race["MRData"]["RaceTable"]["Races"][0]["round"]
        event = fastf1.get_event(2025, int(next_round))

        race = F1Race()
        race.round_number = event["RoundNumber"]
        race.country = event["Country"]
        race.location = event["Location"]
        race.event_name = event["EventName"]
        race.datetime = event["EventDate"]

        for index, value in event.items():
            session_data = self.session_re.findall(index)
            if len(session_data) > 0:
                session_number = int(session_data[0][0])
                if session_data[0][1] == "":
                    race.sessions[session_number].name = value
                else:
                    race.sessions[session_number].date = value

        await ctx.send(embed=race.to_embed())

    @commands.command(name="next2", help="Show countdown to the next F1 Race.")
    async def next_race(self, ctx):
        data = requests.get("https://api.jolpi.ca/ergast/f1/current/next.json").json()
        datetimes = []
        races = data["MRData"]["RaceTable"]["Races"]
        for race in races:
            race_datetime = f"{race['date']} {race['time']}"
            datetimes.append(race_datetime)
            
            for session in ["FirstPractice", "SecondPractice", "ThirdPractice", "Qualifying"]:
                if session in race:
                    session_datetime = f"{race[session]['date']} {race[session]['time']}"
                    datetimes.append(session_datetime)
        
        datetime_objects = [datetime.strptime(dt, "%Y-%m-%d %H:%M:%SZ") for dt in datetimes]
        earliest_datetime = min(datetime_objects)
        earliest_datetime_str = earliest_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        await ctx.send(self.calculate_time_until(earliest_datetime)) 


class F1Race:
    def __init__(self):
        self.round_number = 0
        self.country = ""
        self.location = ""
        self.event_name = ""
        self.sessions = [F1RaceSession() for _ in range(10)]


    @staticmethod
    def make_discord_timestamp(value):
        """
        Build a Discord timestamp from a string or date object
        This is a Unix timestamp that displays a datetime to a Discord user in their localised timezone.
        """
        if isinstance(value, datetime):
            return f"<t:{int(value.timestamp())}:F>"
        if isinstance(value, str):
            return f"<t:{int(datetime.strptime(value, '%b %d %Y %H:%M').timestamp())}:F>"

    def to_embed(self):
        embed = discord.Embed(color=0x9C824A, title=f"Next Race - Round {self.round_number}")
        embed.set_author(
            name="F1 Races",
            icon_url="https://purepng.com/public/uploads/large/purepng.com-formula-1-logoformula-1logonew2018-21529676510t61kq.png",  # noqa
        )
        embed.add_field(name="Country", value=self.country, inline=True)
        embed.add_field(name="Location", value=self.location, inline=True)
        embed.add_field(name="Event Name", value=self.event_name, inline=True)

        for session in self.sessions:
            if session.has_value():
                session_date = self.make_discord_timestamp(session.date.to_pydatetime())
                embed.add_field(name=session.name, value=session_date, inline=False)
        return embed


class F1RaceSession:
    def __init__(self):
        self.name = ""
        self.date = ""

    def has_value(self):
        return self.name != "" and self.date != ""


async def setup(bot):
    await bot.add_cog(F1Cog(bot))