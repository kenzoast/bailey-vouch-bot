import discord
from discord.ext import commands
import requests
from datetime import datetime

class CryptoChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.supported_cryptos = {
            "btc": "bitcoin",
            "sol": "solana", 
            "ltc": "litecoin"
        }

    @commands.slash_command(name="crypto", description="Check the price of BTC, SOL, or LTC.")
    async def crypto(self, ctx: discord.ApplicationContext, symbol: str):
        """
        Check the price of Bitcoin (BTC), Solana (SOL), or Litecoin (LTC).
        """
        symbol = symbol.lower()
        if symbol not in self.supported_cryptos:
            await ctx.respond("Invalid symbol. Use one of the following: BTC, SOL, LTC.", ephemeral=True)
            return

        try:
            # Fetch price data
            params = {
                "ids": self.supported_cryptos[symbol],
                "vs_currencies": "usd"
            }
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException:
            await ctx.respond("Failed to fetch price data. Please try again later.", ephemeral=True)
            return

        # Process the price data
        coin_id = self.supported_cryptos[symbol]
        price_usd = data.get(coin_id, {}).get("usd")
        
        if not price_usd:
            await ctx.respond(f"Price data for {symbol.upper()} is unavailable at the moment.", ephemeral=True)
            return

        # Determine full coin name
        name_map = {
            "bitcoin": "Bitcoin",
            "solana": "Solana",
            "litecoin": "Litecoin"
        }
        name = name_map[coin_id]

        # Create embed for response
        embed = discord.Embed(
            title=f"{name} (Symbol: {symbol.upper()})",
            description=f"**Price (USD):** ${price_usd:,.2f}",
            color=discord.Color.brand_red(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Price data retrieved on")
        
        # Send the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(CryptoChecker(bot))
