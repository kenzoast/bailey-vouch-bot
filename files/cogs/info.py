import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="info", description="Fetch basic information about a user.")
    async def user_info(self, ctx: discord.ApplicationContext, user: discord.User = None):
        """
        Fetch basic information about a user or yourself if no user is specified.
        """
        # Use the provided user or default to the command user
        user = user or ctx.author

        # Create the embed with username, user ID, and profile picture
        embed = discord.Embed(
            title=f"Information about {user.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Username", value=f"{user.name}#{user.discriminator}", inline=False)
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.set_thumbnail(url=user.avatar.url)  # Add the user's profile picture as the thumbnail

        # Respond with the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))
