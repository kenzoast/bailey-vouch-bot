import discord
from discord.ext import commands
import random
import sqlite3

DB_PATH = "fishing_game.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

class Coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_balance(self, user_id):
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        return result[0] if result else 0

    def update_user_balance(self, user_id, amount):
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

    @commands.command(name="coinflip")
    async def coinflip(self, ctx, bet: int, choice: str):
        """Play a coinflip game."""
        user_id = ctx.author.id
        balance = self.get_user_balance(user_id)

        if bet <= 0:
            await ctx.send("Your bet must be greater than $0.")
            return
        if bet > balance:
            await ctx.send("You don't have enough balance to place this bet.")
            return
        if choice.lower() not in ["heads", "tails"]:
            await ctx.send("You must choose 'heads' or 'tails'.")
            return

        result = random.choice(["heads", "tails"])
        if choice.lower() == result:
            self.update_user_balance(user_id, bet)
            outcome = f"The coin landed on **{result}**! You won **${bet}**!"
            color = discord.Color.green()
        else:
            self.update_user_balance(user_id, -bet)
            outcome = f"The coin landed on **{result}**! You lost **${bet}**."
            color = discord.Color.red()

        embed = discord.Embed(
            title="Coin Flip",
            description=outcome,
            color=color
        )
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(user_id)}", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Coinflip(bot))
