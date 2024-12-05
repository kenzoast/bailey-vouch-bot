import os
import subprocess
import discord
from discord.ext import commands
from utils.venv import get_venv_python
import json
import sqlite3
from cogs.maintickets import TicketPanelView
from cogs.maintickets import CloseTicketView

# Load the main bot token from config.json
with open("config.json") as config_file:
    config = json.load(config_file)
    TOKEN = config.get("main_token")

if TOKEN is None:
    raise ValueError("Bot token is not set in the config.json file.")

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

# Function to start all bots in the /bots directory
def start_all_bots():
    bots_folder = "bots"
    
    # Check if the bots folder exists
    if os.path.exists(bots_folder):
        # Iterate through all folders inside /bots
        for bot_folder in os.listdir(bots_folder):
            bot_path = os.path.join(bots_folder, bot_folder)
            
            # Only process directories that contain bot.py
            if os.path.isdir(bot_path) and "bot.py" in os.listdir(bot_path):
                config_path = os.path.join(bot_path, "config.json")
                if not os.path.exists(config_path):
                    print(f"Skipping {bot_folder}: config.json not found.")
                    continue

                # Read the virtual environment name from the config.json, default to 'listing'
                with open(config_path, "r") as config_file:
                    config_data = json.load(config_file)
                    venv_name = config_data.get("venv_name", "listing")  # Default to 'listing'

                # Start the bot using the virtual environment
                try:
                    venv_python = get_venv_python(venv_name)
                    # Start the bot.py using subprocess
                    subprocess.Popen([venv_python, "bot.py"], cwd=bot_path)
                    print(f"Started bot in {bot_folder} using venv {venv_name}")
                except FileNotFoundError:
                    print(f"Python executable for {venv_name} not found in {bot_folder}")
    else:
        print("Bots folder not found.")


@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready!')
    # Start all bots in the /bots folder
    start_all_bots()
    bot.add_view(TicketPanelView(bot, sqlite3.connect("tickets.db"), 1309886590226661478))  # Use actual DB and category ID
    bot.add_view(CloseTicketView(sqlite3.connect("tickets.db")))

bot.load_extension('cogs.bot_setup')
bot.load_extension('cogs.credits')
bot.load_extension('cogs.keys')
bot.load_extension("cogs.userid") 
bot.load_extension('cogs.currency')
bot.load_extension('cogs.purge')
bot.load_extension('cogs.cat')
bot.load_extension('cogs.donate')
bot.load_extension('cogs.rolemanagement')
bot.load_extension('cogs.maintickets')
bot.load_extension('cogs.time')
bot.load_extension('cogs.rockpaperscissors')
bot.load_extension('cogs.skibidi')
bot.load_extension('cogs.coinflip')
bot.load_extension('cogs.avatar')
bot.load_extension('cogs.info')
bot.load_extension('cogs.serverinfo')
bot.load_extension('cogs.cryptochecker')
bot.load_extension('cogs.convertcrypto')


# Run the main bot
bot.run(TOKEN)
