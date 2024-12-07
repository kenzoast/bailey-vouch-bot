import discord
from discord.ext import commands
import random
import sqlite3

DB_PATH = "fishing_game.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

class Dice(commands.Cog):
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

    @commands.command(name="dice")
    async def dice(self, ctx, bet: int):
        """Roll a dice to win or lose money."""
        user_id = ctx.author.id
        balance = self.get_user_balance(user_id)

        if bet <= 0:
            await ctx.send("Your bet must be greater than $0.")
            return
        if bet > balance:
            await ctx.send("You don't have enough balance to place this bet.")
            return

        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if user_roll > bot_roll:
            self.update_user_balance(user_id, bet)
            outcome = f"🎲 You rolled **{user_roll}**, and I rolled **{bot_roll}**. You won **${bet}**!"
            color = discord.Color.green()
        elif user_roll < bot_roll:
            self.update_user_balance(user_id, -bet)
            outcome = f"🎲 You rolled **{user_roll}**, and I rolled **{bot_roll}**. You lost **${bet}**."
            color = discord.Color.red()
        else:
            outcome = f"🎲 You rolled **{user_roll}**, and I rolled **{bot_roll}**. It's a tie! No money lost."
            color = discord.Color.blue()

        embed = discord.Embed(
            title="Dice Roll",
            description=outcome,
            color=color
        )
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(user_id)}", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Dice(bot))
