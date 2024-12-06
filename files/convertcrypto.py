import discord
from discord.ext import commands
import requests

class ConvertCrypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Function to get cryptocurrency prices in USD
    def get_crypto_prices(self):
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,litecoin,solana&vs_currencies=usd'
        response = requests.get(url)
        data = response.json()
        
        # Extract relevant data
        btc_price = data.get('bitcoin', {}).get('usd', 0)
        ltc_price = data.get('litecoin', {}).get('usd', 0)
        sol_price = data.get('solana', {}).get('usd', 0)
        
        return btc_price, ltc_price, sol_price

    # Command to convert USD to crypto
    @commands.command()
    async def convert(self, ctx, amount: float):
        # Get the latest prices from CoinGecko
        btc, ltc, sol = self.get_crypto_prices()

        if btc == 0 or ltc == 0 or sol == 0:
            await ctx.send("Error fetching cryptocurrency prices.")
            return

        # Perform the conversion
        btc_amount = amount / btc
        ltc_amount = amount / ltc
        sol_amount = amount / sol

        # Send the results to the user
        await ctx.send(f"**Conversion Results for ${amount} USD:**\n"
                       f"Bitcoin (BTC): {btc_amount:.6f} BTC\n"
                       f"Litecoin (LTC): {ltc_amount:.6f} LTC\n"
                       f"Solana (SOL): {sol_amount:.6f} SOL")


# Setup function to add the Cog to the bot
def setup(bot):
    bot.add_cog(ConvertCrypto(bot))
