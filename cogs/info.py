import discord
from discord.ext import commands
from discord import Member

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="info", description="Fetch detailed information about a user.")
    async def user_info(self, ctx: discord.ApplicationContext, user: discord.Member = None):
        """
        Fetch detailed information about a user or yourself if no user is specified.
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

        # Add fields for user information
        embed.add_field(name="Username", value=f"{user.name}#{user.discriminator}", inline=False)
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)

        # If the user is in the server, add server-specific info
        if isinstance(user, Member):
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
            roles = ", ".join([role.mention for role in user.roles if role.name != "@everyone"])
            embed.add_field(name="Roles", value=roles if roles else "None", inline=False)
            embed.add_field(name="Top Role", value=user.top_role.mention if user.top_role else "None", inline=False)

        # Add footer
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        
        # Respond with the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))
