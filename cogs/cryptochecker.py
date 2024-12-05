import discord
from discord.ext import commands
import requests
from datetime import datetime

class CryptoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.supported_cryptos = {
            "btc": "bitcoin",
            "sol": "solana", 
            "ltc": "litecoin"
        }
    
    def get_crypto_price(self, symbol):
        """
        Fetch the current price of a given cryptocurrency in USD.
        
        :param symbol: Cryptocurrency symbol (e.g., 'btc', 'sol', 'ltc')
        :return: Price in USD or None if fetching fails
        """
        symbol = symbol.lower()
        if symbol not in self.supported_cryptos:
            return None
        
        try:
            # Fetch price data
            params = {
                "ids": self.supported_cryptos[symbol],
                "vs_currencies": "usd"
            }
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process the price data
            coin_id = self.supported_cryptos[symbol]
            price_usd = data.get(coin_id, {}).get("usd")
            
            return price_usd
        except requests.exceptions.RequestException:
            return None
    
    @commands.slash_command(name="crypto", description="Check the price of BTC, SOL, or LTC.")
    async def crypto(self, ctx: discord.ApplicationContext, symbol: str):
        """
        Check the price of Bitcoin (BTC), Solana (SOL), or Litecoin (LTC).
        """
        symbol = symbol.lower()
        if symbol not in self.supported_cryptos:
            await ctx.respond("Invalid symbol. Use one of the following: BTC, SOL, LTC.", ephemeral=True)
            return
        
        price_usd = self.get_crypto_price(symbol)
        
        if not price_usd:
            await ctx.respond(f"Price data for {symbol.upper()} is unavailable at the moment.", ephemeral=True)
            return
        
        # Determine full coin name
        name_map = {
            "bitcoin": "Bitcoin",
            "solana": "Solana",
            "litecoin": "Litecoin"
        }
        name = name_map[self.supported_cryptos[symbol]]
        
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
    
    @commands.slash_command(name="convert", description="Convert USD to equivalent crypto amount.")
    async def convert(self, ctx: discord.ApplicationContext, amount: float, symbol: str):
        """
        Convert a USD amount to equivalent cryptocurrency amount.
        
        :param amount: USD amount to convert
        :param symbol: Cryptocurrency symbol (BTC, SOL, or LTC)
        """
        symbol = symbol.lower()
        if symbol not in self.supported_cryptos:
            await ctx.respond("Invalid symbol. Use one of the following: BTC, SOL, LTC.", ephemeral=True)
            return
        
        # Get current price
        price_usd = self.get_crypto_price(symbol)
        
        if not price_usd:
            await ctx.respond(f"Price data for {symbol.upper()} is unavailable at the moment.", ephemeral=True)
            return
        
        # Calculate crypto amount
        crypto_amount = amount / price_usd
        
        # Determine full coin name
        name_map = {
            "bitcoin": "Bitcoin",
            "solana": "Solana",
            "litecoin": "Litecoin"
        }
        name = name_map[self.supported_cryptos[symbol]]
        
        # Create embed for response
        embed = discord.Embed(
            title=f"USD to {name} Conversion",
            description=(
                f"**USD Amount:** ${amount:,.2f}\n"
                f"**{name} Price:** ${price_usd:,.2f}\n"
                f"**{name} Amount:** {crypto_amount:,.6f}"
            ),
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Conversion calculated on")
        
        # Send the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(CryptoCog(bot))
