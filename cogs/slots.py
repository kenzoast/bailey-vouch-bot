import discord
from discord.ext import commands
import random
import sqlite3

# Ensure the SQLite database is connected
DB_PATH = "fishing_game.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create the users table if it does not exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
''')
conn.commit()

class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_balance(self, user_id):
        # Ensure the user exists
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        
        # Get user balance
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        return result[0] if result else 0  # Default balance is 0 if no record is found

    def update_user_balance(self, user_id, amount):
        # Insert user if they don't exist
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        
        # Update balance
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

    @commands.command(name="slots")
    async def slots(self, ctx, bet: int):
        """Play the slots game."""
        user_id = ctx.author.id
        balance = self.get_user_balance(user_id)

        if bet <= 0:
            await ctx.send("Your bet must be greater than $0.")
            return
        if bet > balance:
            await ctx.send("You don't have enough balance to place this bet.")
            return

        symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]
        slot_result = [random.choice(symbols) for _ in range(3)]

        if len(set(slot_result)) == 1:  # Jackpot (all symbols are the same)
            winnings = bet * 3
            self.update_user_balance(user_id, winnings)
            outcome = f"🎉 JACKPOT! You won **${winnings}**!"
            color = discord.Color.gold()
        elif len(set(slot_result)) == 2:  # Close (two symbols are the same)
            winnings = int(bet * 1.5)
            self.update_user_balance(user_id, winnings)
            outcome = f"👏 Close! You won **${winnings}**!"
            color = discord.Color.blue()
        else:  # No match
            self.update_user_balance(user_id, -bet)
            outcome = f"😢 Better luck next time! You lost **${bet}**."
            color = discord.Color.red()

        # Create and send the embed message
        embed = discord.Embed(
            title="🎰 Slots Machine",
            description=f"Result: {' '.join(slot_result)}\n\n{outcome}",
            color=color
        )
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(user_id)}", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Slots(bot))
