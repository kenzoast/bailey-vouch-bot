import discord
from discord.ext import commands

class Donation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="donate", description="Get donation information.")
    async def donate(self, ctx):
        donation_info = (
            "💰 **Paypal Donations:** for any paypal donations you can donate to scubasservices @outlook.com but we much perfer crypto donations\n"
            "💳 **Crypto Donations:** To donate with crypto send to this address: LKRM3Nii8WwuWTturgh6nq41zuZfgnficZ)\n"
            "**Custom roles:** If you donate more than 5$ to the crypto wallet or 10$ to the paypal account you can get your own custom role with your own custom color!\n"
            "**/skibidi list:** If you donate more than 1$ to either you can get on the sigma list!"
        )
        await ctx.respond(donation_info, ephemeral=True)

def setup(bot):
    bot.add_cog(Donation(bot))
