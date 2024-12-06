import discord
from discord.ext import commands
import random

class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="coinflip", description="Flip a coin and see the result!")
    async def coinflip(self, ctx: discord.ApplicationContext):
        """
        Flip a coin and show the result.
        """
        # Randomly pick between Heads and Tails
        result = random.choice(["Heads", "Tails"])
        
        # Create an embed for the result
        embed = discord.Embed(
            title="Coin Flip",
            description=f"The coin landed on **{result}**!",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Powered by discord.gg/bailey!")
        
        # Respond with the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(CoinFlip(bot))
