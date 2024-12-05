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
            "ltc": "litecoin",
            "eth": "ethereum",
            "doge": "dogecoin"
        }

    @commands.command(name="crypto")
    async def crypto_command(self, ctx, symbol: str = None):
        """
        Check cryptocurrency prices in any chat channel.
        Usage: !crypto <symbol>
        Supported symbols: BTC, SOL, LTC, ETH, DOGE
        """
        if not symbol:
            await ctx.send("Please specify a cryptocurrency symbol. Supported: " + 
                           ", ".join(symbol.upper() for symbol in self.supported_cryptos.keys()))
            return

        symbol = symbol.lower()
        if symbol not in self.supported_cryptos:
            await ctx.send("Invalid symbol. Use one of the following: " + 
                           ", ".join(symbol.upper() for symbol in self.supported_cryptos.keys()))
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
            await ctx.send("Failed to fetch price data. Please try again later.")
            return

        # Process the price data
        coin_id = self.supported_cryptos[symbol]
        price_usd = data.get(coin_id, {}).get("usd")
        
        if not price_usd:
            await ctx.send(f"Price data for {symbol.upper()} is unavailable at the moment.")
            return

        # Determine full coin name
        name_map = {
            "bitcoin": "Bitcoin",
            "solana": "Solana",
            "litecoin": "Litecoin",
            "ethereum": "Ethereum",
            "dogecoin": "Dogecoin"
        }
        name = name_map[coin_id]

        # Create embed for response
        embed = discord.Embed(
            title=f"{name} (Symbol: {symbol.upper()})",
            description=f"**Price (USD):** ${price_usd:,.2f}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Price data retrieved on")
        
        # Send the embed
        await ctx.send(embed=embed)

    @commands.slash_command(name="crypto", description="Check the price of cryptocurrencies.")
    async def crypto_slash(self, ctx: discord.ApplicationContext, symbol: str):
        """
        Slash command version of the crypto price checker
        """
        # Reuse the same logic as the text command
        await self.crypto_command(ctx, symbol)

def setup(bot):
    bot.add_cog(CryptoChecker(bot))
