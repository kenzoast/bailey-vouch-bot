import discord
from discord.ext import commands

class SkibidiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # List of allowed Discord IDs
        self.sigma_ids = [1264623647671451679, 450331258094878730, 761654350086799410, 1155798723515920404, 1280152659134775299, 571951965500735498, 1292032485601050667, 881599312449118209, 1242588844688408681, 1169382966535925902, 1288177542750142658, 1235525090108641311]  # Replace with your desired IDs

    @discord.slash_command(name="skibidi", description="Check if you're sigma.")
    async def skibidi(self, ctx: discord.ApplicationContext):
        # Check if the user's ID is in the sigma_ids list
        if ctx.author.id in self.sigma_ids:
            embed = discord.Embed(
                title="Sigma Alert",
                color=discord.Color.green()
            )
            embed.add_field(name="User", value=f"{ctx.author}", inline=True)
            embed.add_field(name="User ID", value=f"{ctx.author.id}", inline=True)
            embed.add_field(name="Sigma", value=f"True", inline=False)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            await ctx.respond("You're not sigma...", ephemeral=True)

# Setup function to add the cog
def setup(bot):
    bot.add_cog(SkibidiCog(bot))
