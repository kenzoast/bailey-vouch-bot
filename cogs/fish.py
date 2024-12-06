import discord
from discord.ext import commands
import random
import sqlite3
import os

# Connect to SQLite database (creates it if it doesn't exist)
DB_PATH = "fishing_game.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create the necessary database tables
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    fish_inventory TEXT DEFAULT '{}'
)
""")
conn.commit()

class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def update_user_balance(self, user_id, amount):
        """Update the user's balance by a specified amount."""
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

    def get_user_balance(self, user_id):
        """Retrieve the user's balance."""
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        return result[0] if result else 0

    def update_inventory(self, user_id, fish):
        """Add fish to the user's inventory."""
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        c.execute("SELECT fish_inventory FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        inventory = eval(result[0]) if result and result[0] else {}
        inventory[fish] = inventory.get(fish, 0) + 1
        c.execute("UPDATE users SET fish_inventory = ? WHERE user_id = ?", (str(inventory), user_id))
        conn.commit()

    def get_inventory(self, user_id):
        """Retrieve the user's inventory."""
        c.execute("SELECT fish_inventory FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        return eval(result[0]) if result and result[0] else {}

    @commands.slash_command(name="fish", description="Go fishing and catch some fish!")
    async def fish(self, ctx):
        """Fish for random fish and earn money."""
        fish_rarities = {
            "Common Fish": {"chance": 50, "value": 10},
            "Uncommon Fish": {"chance": 30, "value": 25},
            "Rare Fish": {"chance": 15, "value": 50},
            "Epic Fish": {"chance": 4, "value": 100},
            "Legendary Fish": {"chance": 1, "value": 250},
        }

        # Determine which fish is caught based on chances
        fish_pool = []
        for fish, info in fish_rarities.items():
            fish_pool.extend([fish] * info["chance"])
        caught_fish = random.choice(fish_pool)

        # Update inventory
        self.update_inventory(ctx.author.id, caught_fish)

        # Create an embed with the fishing result
        embed = discord.Embed(
            title="🎣 Fishing Result",
            description=f"You caught a **{caught_fish}**!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Fish Value", value=f"${fish_rarities[caught_fish]['value']}", inline=False)
        embed.set_footer(text="Keep fishing to earn more money!")

        await ctx.respond(embed=embed)

    @commands.slash_command(name="sell", description="Sell all your fish for money.")
    async def sell(self, ctx):
        """Sell all fish in the user's inventory."""
        inventory = self.get_inventory(ctx.author.id)
        if not inventory:
            embed = discord.Embed(
                title="No Fish to Sell",
                description="You don't have any fish to sell. Go fishing first!",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
            return

        fish_rarities = {
            "Common Fish": 10,
            "Uncommon Fish": 25,
            "Rare Fish": 50,
            "Epic Fish": 100,
            "Legendary Fish": 250,
        }

        total_earnings = 0
        for fish, count in inventory.items():
            total_earnings += fish_rarities.get(fish, 0) * count

        # Update balance and clear inventory
        self.update_user_balance(ctx.author.id, total_earnings)
        c.execute("UPDATE users SET fish_inventory = '{}' WHERE user_id = ?", (ctx.author.id,))
        conn.commit()

        # Create an embed with the sell result
        embed = discord.Embed(
            title="💰 Fish Sold",
            description=f"You sold all your fish for **${total_earnings}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(ctx.author.id)}", inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="balance", description="Check your current balance.")
    async def balance(self, ctx):
        """Check the user's current balance."""
        balance = self.get_user_balance(ctx.author.id)
        embed = discord.Embed(
            title="💵 Your Balance",
            description=f"You currently have **${balance}**.",
            color=discord.Color.gold()
        )
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Fishing(bot))
