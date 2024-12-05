import discord
from discord.ext import commands
import requests
from datetime import datetime

class CryptoConversionCog(commands.Cog):
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
    
    @commands.slash_command(name="usdtocrypto", description="Convert USD to multiple cryptocurrencies.")
    async def usd_to_crypto(self, ctx: discord.ApplicationContext, amount: float):
        """
        Convert a USD amount to equivalent amounts of multiple cryptocurrencies.
        
        :param amount: USD amount to convert
        """
        # Create embed for conversion results
        embed = discord.Embed(
            title="USD Cryptocurrency Conversion",
            description=f"**USD Amount:** ${amount:,.2f}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Track whether any conversions were successful
        conversion_successful = False
        
        # Perform conversions for each supported cryptocurrency
        for symbol, coin_id in self.supported_cryptos.items():
            price_usd = self.get_crypto_price(symbol)
            
            if price_usd:
                # Calculate crypto amount
                crypto_amount = amount / price_usd
                
                # Determine full coin name
                name_map = {
                    "bitcoin": "Bitcoin",
                    "solana": "Solana",
                    "litecoin": "Litecoin"
                }
                name = name_map[coin_id]
                
                # Add conversion to embed
                embed.add_field(
                    name=f"{name} ({symbol.upper()})",
                    value=f"**Amount:** {crypto_amount:,.6f}\n**Price:** ${price_usd:,.2f}",
                    inline=True
                )
                
                conversion_successful = True
        
        if not conversion_successful:
            await ctx.respond("Unable to fetch cryptocurrency prices at the moment.", ephemeral=True)
            return
        
        embed.set_footer(text="Conversion calculated on")
        
        # Send the embed
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(CryptoConversionCog(bot))
