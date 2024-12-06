import discord
from discord.ext import commands
import pytz
from datetime import datetime

class Time(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(name='time', description='Check the current time in a specified country.')
    async def what_time(self, ctx: discord.ApplicationContext, country: str):
        """
        Responds with the current time in the specified country.
        """
        timezones = {
            'usa': 'America/New_York',
            'us': 'America/New_York',
            'united states': 'America/New_York',
            'uk': 'Europe/London',
            'australia': 'Australia/Sydney',
            'canada': 'America/Toronto',
            'germany': 'Europe/Berlin',
            'france': 'Europe/Paris',
            'japan': 'Asia/Tokyo',
            'china': 'Asia/Shanghai',
            'india': 'Asia/Kolkata',
            'brazil': 'America/Sao_Paulo',
            'south africa': 'Africa/Johannesburg',
            'russia': 'Europe/Moscow',
            'south korea': 'Asia/Seoul',
            'italy': 'Europe/Rome',
            'spain': 'Europe/Madrid',
            'poland': 'Europe/Warsaw',
            'mexico': 'America/Mexico_City',
            'turkey': 'Europe/Istanbul',
            'thailand': 'Asia/Bangkok',
            'vietnam': 'Asia/Ho_Chi_Minh',
            'philippines': 'Asia/Manila',
            'malaysia': 'Asia/Kuala_Lumpur',
            'singapore': 'Asia/Singapore',
            'new zealand': 'Pacific/Auckland',
        }

        # Get the timezone
        timezone = timezones.get(country.lower())
        if timezone is None:
            await ctx.respond(f"Sorry, I don't have the timezone information for '{country}'. Please use a contry from this list: Usa, Uk, australia, canada, germany, france, japan, china, india, brazil, south africa, russia, south korea, italy, spain, poland, mexico, turkey, thailand, vietnam, philippines, singapore, malaysia, new zealand,", ephemeral=True)
            return

        # Get the current time
        current_time = datetime.now(pytz.timezone(timezone))
        time_str = current_time.strftime("%H:%M:%S %Z%z")

        # Create an embed to display the time
        embed = discord.Embed(
            title=f'Current Time in {country.capitalize()}',
            description=time_str,
            color=discord.Color.yellow()
        )
        embed.set_footer(text='Powered by discord.gg/bailey')
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Time(bot))
