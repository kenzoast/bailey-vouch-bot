import discord
from discord.ext import commands
from views.configure_view import ConfigureView
from wrappers.embedWrapper import create_embed
import constants

OWNER_ID = constants.OWNER_ID
class ConfigureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command for /configure
    @commands.slash_command(name="configure", description="Configure the bot settings")
    async def configure(self, ctx):
        # Check if the user is the owner
        if ctx.author.id != OWNER_ID:
            error_embed = create_embed(
                title="Permission Denied",
                description="You must be the bot owner to use this command.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        embed = create_embed(
            title="Bot Configuration",
            description="Use the buttons below to configure the bot.",
            color=discord.Color.blue()
        )
        view = ConfigureView(self.bot)
        await ctx.respond(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(ConfigureCog(bot))
