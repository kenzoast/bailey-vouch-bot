import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="serverinfo", description="Get information about the server.")
    async def server_info(self, ctx: discord.ApplicationContext):
        """
        Provide information about the server, including member count, bot count, and boost tier.
        """
        # Ensure the command is used in a guild
        if not ctx.guild:
            await ctx.respond("This command can only be used in a server.", ephemeral=True)
            return

        # Get server details
        server = ctx.guild
        total_members = server.member_count
        bots = len([member for member in server.members if member.bot])
        boost_tier = server.premium_tier

        # Create the embed
        embed = discord.Embed(
            title=f"Information about {server.name}",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=server.icon.url if server.icon else None)
        embed.add_field(name="Total Members", value=str(total_members), inline=False)
        embed.add_field(name="Bot Count", value=str(bots), inline=False)
        embed.add_field(name="Boost Tier", value=f"Level {boost_tier}" if boost_tier > 0 else "No Boosts", inline=False)
        embed.set_footer(text=f"Server ID: {server.id}")

        # Respond with the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(ServerInfo(bot))
