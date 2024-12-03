import discord
from discord.ext import commands
import os
import constants

BOT_TOKEN = constants.BOT_TOKEN
BOT_PREFIX = constants.BOT_PREFIX
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready!')
    activity = discord.CustomActivity(name="you use discord.gg/bailey")  # Shows as "Playing with code"
    # Set the activity and status
    await bot.change_presence(status=discord.Status.online, activity=activity)
    bot.add_view(ListViews())
    
# Load cogs from the cogs directory
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(BOT_TOKEN)
