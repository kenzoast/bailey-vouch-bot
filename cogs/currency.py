import discord
from discord.ext import commands
import requests

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://v6.exchangerate-api.com/v6/b780f7dddd2230b05f4dbbe7/latest/"
        self.currencies = {
            "EUR": "Euro",
            "USD": "United States Dollar",
            "GBP": "British Pound",
            "JPY": "Japanese Yen",
            "CNY": "Chinese Yuan"
        }

    @commands.slash_command(name="convert", description="Convert an amount of one currency to another.")
    async def convert(self, ctx, amount: float, from_currency: str, to_currency: str):
        """Convert an amount of one currency to another."""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency not in self.currencies or to_currency not in self.currencies:
            embed = discord.Embed(
                title="Invalid Currency",
                description=f"Please use one of the following currencies:\n{', '.join(self.currencies.keys())}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        try:
            response = requests.get(self.api_url + from_currency)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to retrieve exchange rates. Please try again later.\nError: {e}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        except ValueError:
            embed = discord.Embed(
                title="Error",
                description="Failed to parse exchange rates. Please try again later.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if "conversion_rates" not in data:
            embed = discord.Embed(
                title="Error",
                description="Failed to retrieve exchange rates. Please try again later.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        exchange_rate = data["conversion_rates"].get(to_currency)
        if not exchange_rate:
            embed = discord.Embed(
                title="Error",
                description=f"Exchange rate for {to_currency} not available.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        result = amount * exchange_rate

        embed = discord.Embed(
            title="Currency Conversion",
            description=f"Exchange rate retrieved successfully!",
            color=discord.Color.green()
        )
        embed.add_field(name="Amount", value=f"{amount} {self.currencies[from_currency]}", inline=True)
        embed.add_field(name="Converted To", value=f"{to_currency} ({self.currencies[to_currency]})", inline=True)
        embed.add_field(name="Result", value=f"{result:.2f} {self.currencies[to_currency]}", inline=False)
        embed.set_footer(text="Data provided by ExchangeRate-API | Accurate at the time of query.")

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Currency(bot))
