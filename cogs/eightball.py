import discord
from discord.ext import commands
import random

class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="8ball", description="Ask the Magic 8-Ball a question!")
    async def eight_ball(self, ctx: discord.ApplicationContext, question: str):
        """
        Responds with a random Magic 8-Ball answer.
        """
        responses = [
            "It is certain.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]

        answer = random.choice(responses)

        embed = discord.Embed(
            title="🎱 The Magic 8-Ball",
            description=f"**Your Question:** {question}\n**Answer:** {answer}",
            color=discord.Color.brand_red()
        )
        embed.set_footer(text="The Magic 8-Ball has spoken!")

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(EightBall(bot))
