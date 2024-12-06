import discord
from discord.ext import commands
import random
import sqlite3

# Connect to SQLite database (creates it if it doesn't exist)
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

class Blackjack(commands.Cog):
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

    def calculate_hand_value(self, hand):
        """Calculate the value of a hand in blackjack."""
        value = 0
        aces = 0
        for card in hand:
            if card in ["J", "Q", "K"]:
                value += 10
            elif card == "A":
                value += 11
                aces += 1
            else:
                value += int(card)

        # Adjust for aces if value exceeds 21
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def draw_card(self):
        """Draw a random card."""
        suits = ["♠", "♥", "♦", "♣"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        return f"{random.choice(ranks)}{random.choice(suits)}"

    @commands.slash_command(name="blackjack", description="Play a game of blackjack.")
    async def blackjack(self, ctx, bet: int):
        """Blackjack game where users can bet."""
        user_id = ctx.author.id
        balance = self.get_user_balance(user_id)

        # Check if the user has enough balance
        if bet <= 0:
            await ctx.respond("Your bet must be greater than 0.", ephemeral=True)
            return
        if bet > balance:
            await ctx.respond("You don't have enough balance to place this bet.", ephemeral=True)
            return

        # Dealer and player initial hands
        dealer_hand = [self.draw_card(), self.draw_card()]
        player_hand = [self.draw_card(), self.draw_card()]

        dealer_value = self.calculate_hand_value([card[:-1] for card in dealer_hand])
        player_value = self.calculate_hand_value([card[:-1] for card in player_hand])

        # Determine the result
        if player_value > 21:
            result = "Bust! You lose."
            winnings = -bet
        elif dealer_value > 21 or player_value > dealer_value:
            result = "You win!"
            winnings = bet
        elif player_value == dealer_value:
            result = "It's a tie!"
            winnings = 0
        else:
            result = "You lose."
            winnings = -bet

        # Update balance
        self.update_user_balance(user_id, winnings)

        # Create an embed for the result
        embed = discord.Embed(
            title="🎲 Blackjack Result",
            color=discord.Color.green() if winnings > 0 else discord.Color.red()
        )
        embed.add_field(name="Dealer's Hand", value=f"{' '.join(dealer_hand)} ({dealer_value})", inline=False)
        embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=False)
        embed.add_field(name="Result", value=result, inline=False)
        embed.add_field(name="Bet", value=f"${bet}", inline=True)
        embed.add_field(name="Winnings", value=f"${winnings if winnings >= 0 else -winnings}", inline=True)
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(user_id)}", inline=False)

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Blackjack(bot))
