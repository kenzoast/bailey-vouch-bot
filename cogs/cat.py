import discord
from discord.ext import commands
import aiohttp
import time

class Cat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="cat", 
        description="Get a random cute cat picture!",
        integration_types={discord.IntegrationType.user_install, discord.IntegrationType.guild_install}
    )
    async def cat(self, ctx: discord.ApplicationContext):
        """Fetch and send a random cute cat picture."""
        timestamp = int(time.time() * 1000)  # Current time in milliseconds
        url = f"https://cataas.com/cat/cute?timestamp={timestamp}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    await ctx.respond(url)
                else:
                    await ctx.respond("Couldn't fetch a cat picture. Try again later!")

def setup(bot):
    bot.add_cog(Cat(bot))
