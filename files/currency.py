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

    @commands.slash_command(name="convert", integration_types={discord.IntegrationType.user_install, discord.IntegrationType.guild_install})
    async def convert(self, ctx, amount: float, from_currency: str, to_currency: str):
        """Convert an amount of one currency to another."""
        if from_currency.upper() not in self.currencies or to_currency.upper() not in self.currencies:
            await ctx.send("Invalid currency. Please use one of the following: " + ", ".join(self.currencies.keys()))
            return

        try:
            response = requests.get(self.api_url + from_currency.upper())
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve exchange rates. Error: {e}")
            return
        except ValueError:
            await ctx.send("Failed to parse exchange rates. Please try again later.")
            return

        if "conversion_rates" not in data:
            await ctx.send("Failed to retrieve exchange rates.")
            return

        exchange_rate = data["conversion_rates"][to_currency.upper()]
        result = amount * exchange_rate

        await ctx.respond(f"{amount} {self.currencies[from_currency.upper()]} is equal to {result:.2f} {self.currencies[to_currency.upper()]}")

def setup(bot):
    bot.add_cog(Currency(bot))