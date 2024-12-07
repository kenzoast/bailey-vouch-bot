import discord
from discord.ext import commands
import random
import sqlite3

# Connect to SQLite database
DB_PATH = "fishing_game.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Ensure the users table exists
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

    def get_user_balance(self, user_id):
        """Retrieve the user's balance from the database."""
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        return result[0] if result else 0

    def update_user_balance(self, user_id, amount):
        """Update the user's balance."""
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.slash_command(name="fish", description="Go fishing to earn money!")
    async def fish(self, ctx):
        """Fishing command with a cooldown."""
        user_id = ctx.author.id

        # Define fish and rewards
        fish_types = {
            "Common Fish": (1, 10),
            "Uncommon Fish": (11, 30),
            "Rare Fish": (31, 60),
            "Epic Fish": (61, 90),
            "Legendary Fish": (91, 100),
        }
        fish_weights = {
            "Common Fish": 60,
            "Uncommon Fish": 25,
            "Rare Fish": 10,
            "Epic Fish": 4,
            "Legendary Fish": 1,
        }

        # Choose a random fish based on weighted probabilities
        fish = random.choices(
            population=list(fish_types.keys()),
            weights=list(fish_weights.values()),
            k=1
        )[0]

        # Calculate reward
        reward = random.randint(*fish_types[fish])

        # Update user's balance
        self.update_user_balance(user_id, reward)
        new_balance = self.get_user_balance(user_id)

        # Create an embed for the result
        embed = discord.Embed(title="🎣 Fishing Result", color=discord.Color.blurple())
        embed.add_field(name="You caught a", value=f"**{fish}**!", inline=False)
        embed.add_field(name="You earned", value=f"${reward}", inline=True)
        embed.add_field(name="Your new balance", value=f"${new_balance}", inline=True)

        await ctx.respond(embed=embed)

    @fish.error
    async def fish_error(self, ctx, error):
        """Handle errors for the fishing command."""
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = int(error.retry_after)
            await ctx.respond(
                f"🕒 You need to wait {retry_after} seconds before fishing again!",
                ephemeral=True
            )
        else:
            raise error

def setup(bot):
    bot.add_cog(Fishing(bot))
