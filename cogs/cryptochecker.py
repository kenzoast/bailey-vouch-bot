import discord
from discord.ext import commands
import requests
from datetime import datetime

class CryptoChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "7ba79e3850214db8a098bb30d95cdcc8"  # Replace with your BlockCypher API key
        self.api_urls = {
            "btc": f"https://api.blockcypher.com/v1/btc/main?token={self.api_key}",
            "ltc": f"https://api.blockcypher.com/v1/ltc/main?token={self.api_key}",
            "sol": "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        }

    @commands.slash_command(name="crypto", description="Check the price of BTC, SOL, or LTC.")
    async def crypto(self, ctx: discord.ApplicationContext, symbol: str):
        """
        Check the price of Bitcoin (BTC), Solana (SOL), or Litecoin (LTC).
        """
        symbol = symbol.lower()

        if symbol not in self.api_urls:
            await ctx.respond("Invalid symbol. Use one of the following: BTC, SOL, LTC.", ephemeral=True)
            return

        try:
            # Fetch price data
            response = requests.get(self.api_urls[symbol])
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            await ctx.respond("Failed to fetch price data. Please try again later.", ephemeral=True)
            return

        # Process the price data
        if symbol in ["btc", "ltc"]:
            price_usd = data.get("usd", {}).get("rate", None)  # Modify if API response structure changes
            name = "Bitcoin" if symbol == "btc" else "Litecoin"
        elif symbol == "sol":
            price_usd = data.get("solana", {}).get("usd", None)
            name = "Solana"

        if not price_usd:
            await ctx.respond(f"Price data for {symbol.upper()} is unavailable at the moment.", ephemeral=True)
            return

        # Create embed for response
        embed = discord.Embed(
            title=f"{name} (Symbol: {symbol.upper()})",
            description=f"**Price (USD):** ${price_usd:,.2f}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Price data retrieved on")

        # Send the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(CryptoChecker(bot))
