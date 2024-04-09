import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

from study_cog import StudyBot

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

INTENTS = discord.Intents.all()

bot = commands.Bot(command_prefix='?', intents=INTENTS)
bot.remove_command('help')

bot.add_cog(StudyBot(bot))

@bot.event
async def on_ready():
    print("okie dokie")

bot.run(TOKEN)
