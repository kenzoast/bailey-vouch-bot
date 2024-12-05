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

        # Embed fields for user information
        embed = discord.Embed(
            title=f"Information about {user.name}",
            color=discord.Color.blue(),
            timestamp=ctx.created_at
        )
        embed.set_thumbnail(url=user.avatar.url)  # Add user's avatar as the thumbnail

        # Add fields for basic user information
        embed.add_field(name="Username", value=f"{user.name}#{user.discriminator}", inline=False)
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)

        # Add footer
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        
        # Respond with the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))
