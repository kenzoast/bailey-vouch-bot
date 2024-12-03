import discord
from discord.ext import commands
from discord import Option
from utils import database
from wrappers.embedWrapper import create_embed
from views.lookup_view import LookupView

class LookupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="lookup", description="Look up a user's vouches")
    async def lookup(
        self,
        ctx,
        user: Option(discord.User, "Select a user to look up", required=False)
    ):
        await ctx.defer(ephemeral=True)
        target_user = user or ctx.author  # If no user is specified, use the command invoker

        # Get the user's vouches from the database
        vouches = database.get_user_vouches(target_user.id)
        if not vouches:
            embed = create_embed(
                title="No Vouches Found",
                description=f"{target_user.mention} has no vouches.",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Create and send the lookup embed with pagination
        view = LookupView(self.bot, target_user, vouches)
        embed = view.get_current_embed()
        await ctx.respond(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(LookupCog(bot))
