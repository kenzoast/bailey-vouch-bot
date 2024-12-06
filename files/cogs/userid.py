import discord
from discord.ext import commands

class UserInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="get-user-id", description="Get your user ID.")
    async def get_user_id(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Your user ID: {ctx.author.id}", ephemeral=True)

# To add the cog to your bot:
def setup(bot):
    bot.add_cog(UserInfoCog(bot))
