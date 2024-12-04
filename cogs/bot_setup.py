import os
import shutil
import subprocess
import json
import discord
from discord.commands import slash_command
from discord.ext import commands
from discord.ui import View, Button
from utils.database import init_db
from utils.venv import get_venv_python
from discord.errors import HTTPException, LoginFailure

# Initialize the database connection
conn, c = init_db()

class BotSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_credits(self, user_id):
        """Load credits from the database"""
        c.execute('SELECT credits FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        if result:
            return result[0]
        return 0  # Default to 0 credits if not found

    def update_credits(self, user_id, credits):
        """Update credits in the database"""
        c.execute('INSERT OR REPLACE INTO users (user_id, credits) VALUES (?, ?)', (user_id, credits))
        conn.commit()

    @slash_command(name="create", description="Set up a new bot with configurations")
    async def setup_bot(self, ctx, 
                        token: str,
                        owner_id: str):
        # Check if the user has enough credits
        user_credits = self.load_credits(ctx.author.id)
        if user_credits <= 0:
            embed = discord.Embed(title="Insufficient Credits", description="You don't have enough credits to create a bot.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Display a confirmation with buttons
        embed = discord.Embed(
            title="Confirm Bot Creation",
            description="Are you sure you want to create and start a new bot? This action will deduct 1 credit from your account.",
            color=discord.Color.blue()
        )

        view = View()

        # Proceed button
        proceed_button = Button(label="Proceed", style=discord.ButtonStyle.green)
        back_button = Button(label="Back", style=discord.ButtonStyle.red)

        async def proceed_callback(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("You are not authorized to perform this action.", ephemeral=True)
                return

            try:
                # Create the folder for the new bot
                bot_name = f"bot_{ctx.author.id}"  # Generate a unique folder name
                new_bot_folder = os.path.join("bots", bot_name)
                os.makedirs(new_bot_folder, exist_ok=True)

                # Copy all files and directories from "files" folder to the new bot folder
                files_folder = "files"
                if os.path.exists(files_folder):
                    for item_name in os.listdir(files_folder):
                        source_item = os.path.join(files_folder, item_name)
                        destination_item = os.path.join(new_bot_folder, item_name)
                        
                        if os.path.isfile(source_item):
                            shutil.copy2(source_item, destination_item)
                        elif os.path.isdir(source_item):
                            if os.path.exists(destination_item):
                                shutil.rmtree(destination_item)
                            shutil.copytree(source_item, destination_item)
                else:
                    await interaction.response.send_message(f"Error: Could not find the 'files' folder", ephemeral=True)
                    return

                # Create config.json with the provided parameters
                config_path = os.path.join(new_bot_folder, "config.json")
                config_data = {
                    "token": token,
                    "owner_id": int(owner_id)
                }

                with open(config_path, "w") as config_file:
                    json.dump(config_data, config_file)

                # Ensure the config.json and bot.py exist before starting the bot
                bot_file_name = "bot.py"
                
                if os.path.exists(os.path.join(new_bot_folder, bot_file_name)) and os.path.exists(config_path):
                    # Get the Python executable from the virtual environment
                    try:
                        venv_name = "venv"  # Replace with your default venv name
                        venv_python = get_venv_python(venv_name)
                    except FileNotFoundError as e:
                        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
                        return
                    
                    # Validate the bot token and intents first
                    test_bot = discord.Client(intents=discord.Intents.default())
                    
                    try:
                        await test_bot.login(token)  # Attempt to log in
                        await test_bot.close()
                    except LoginFailure:
                        embed = discord.Embed(
                            title="Invalid Token",
                            description="The bot token you provided is invalid. Please provide a valid token.",
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        shutil.rmtree(new_bot_folder)  # Clean up if bot creation fails
                        return
                    except discord.PrivilegedIntentsRequired:
                        embed = discord.Embed(
                            title="Intent Error",
                            description="Your bot token is valid, but intents required to run the bot are disabled. Please enable the required intents (e.g., 'Server Members Intent') in the Discord Developer Portal.",
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        shutil.rmtree(new_bot_folder)  # Clean up if bot creation fails
                        return
                    except Exception as e:
                        embed = discord.Embed(
                            title="Login Error",
                            description=f"An unexpected error occurred during login: {str(e)}",
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        shutil.rmtree(new_bot_folder)  # Clean up if bot creation fails
                        return
                    
                    # If token and intents are valid, proceed to run the bot in subprocess
                    try:
                        subprocess.Popen([venv_python, bot_file_name], cwd=new_bot_folder)

                        # Deduct credits since everything went well
                        self.update_credits(ctx.author.id, user_credits - 1)

                        embed = discord.Embed(
                            title="Bot Creation Success",
                            description=f"Bot `{bot_name}` has been created and started! You have {user_credits - 1} credits left.",
                            color=discord.Color.green()
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    except Exception as e:
                        embed = discord.Embed(
                            title="Error",
                            description=f"An error occurred while starting the bot: {str(e)}",
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        shutil.rmtree(new_bot_folder)  # Clean up if bot creation fails
                else:
                    await interaction.response.send_message(f"Error: Could not find {bot_file_name} or {config_path}", ephemeral=True)
            except Exception as e:
                embed = discord.Embed(
                    title="Setup Failed",
                    description=f"An unexpected error occurred: {str(e)}",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        async def back_callback(interaction):
            if interaction.user.id == ctx.author.id:
                await interaction.response.send_message("Bot creation has been canceled.", ephemeral=True)
            view.stop()

        proceed_button.callback = proceed_callback
        back_button.callback = back_callback

        view.add_item(proceed_button)
        view.add_item(back_button)

        await ctx.respond(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(BotSetup(bot))
