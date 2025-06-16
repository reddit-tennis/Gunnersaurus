import logging
import os

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=os.environ.get('prefix'), intents=intents)

    async def startup(self):
        await bot.wait_until_ready()
        # await bot.tree.sync()
        await bot.change_presence(activity=discord.Game(name='Serving'))
        # logger.info('Successfully synced applications commands')
        logger.info(f'Connected as {bot.user}')

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    logger.info(f"Loaded {filename}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}")
                    logger.error(f"[ERROR] {e}")

        self.loop.create_task(self.startup())

bot = Bot()
bot.run(os.environ.get('token'))
