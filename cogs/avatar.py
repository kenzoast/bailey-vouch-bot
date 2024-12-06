import discord
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="avatar", description="Fetch a user's profile picture.")
    async def avatar(self, ctx: discord.ApplicationContext, user: discord.User = None):
        """
        Fetch the profile picture of a user or yourself if no user is specified.
        """
        # Use the provided user or default to the command user
        user = user or ctx.author

        # Create the embed
        embed = discord.Embed(
            title=f"This is {user.name}'s profile picture.",
            color=discord.Color.brand_red()
        )
        embed.set_image(url=user.avatar.url)  # Attach the user's avatar
        embed.set_footer(text="Thanks for using the Avatar command!")
        
        # Respond with the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Avatar(bot))
