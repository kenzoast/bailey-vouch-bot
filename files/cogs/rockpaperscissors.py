import discord
from discord.ext import commands
import random

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="rps", description="Play Rock, Paper, Scissors with the bot!")
    async def rps(self, ctx: discord.ApplicationContext, user_choice: str):
        """
        Play Rock, Paper, Scissors against the bot with fair randomness.
        """
        user_choice = user_choice.lower()
        choices = ["rock", "paper", "scissors"]

        # Validate user's choice
        if user_choice not in choices:
            await ctx.respond("Invalid choice! Please choose rock, paper, or scissors.", ephemeral=True)
            return

        # Random choice for the bot
        bot_choice = random.choice(choices)

        # Determine the result
        if user_choice == bot_choice:
            result_message = "It's a tie! 🤝"
            color = discord.Color.gold()
        elif (user_choice == "rock" and bot_choice == "scissors") or \
             (user_choice == "paper" and bot_choice == "rock") or \
             (user_choice == "scissors" and bot_choice == "paper"):
            result_message = "You win! 😢 Congratulations."
            color = discord.Color.green()
        else:
            result_message = "I win! Better luck next time 😈"
            color = discord.Color.red()

        # Create an embed for the result
        embed = discord.Embed(
            title="Rock, Paper, Scissors",
            description=f"You chose: **{user_choice.capitalize()}**\nBot chose: **{bot_choice.capitalize()}**",
            color=color
        )
        embed.add_field(name="Result", value=result_message)
        embed.set_footer(text="powered by discord.gg/bailey!")
        
        # Respond with the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(RockPaperScissors(bot))
