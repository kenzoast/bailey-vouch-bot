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
        """Start a Blackjack game with betting and interactions."""
        user_id = ctx.author.id
        balance = self.get_user_balance(user_id)

        # Check if the user has enough balance
        if bet <= 0:
            await ctx.respond("Your bet must be greater than 0.", ephemeral=True)
            return
        if bet > balance:
            await ctx.respond("You don't have enough balance to place this bet.", ephemeral=True)
            return

        # Initialize dealer and player hands
        dealer_hand = [self.draw_card(), self.draw_card()]
        player_hand = [self.draw_card(), self.draw_card()]

        dealer_value = self.calculate_hand_value([card[:-1] for card in dealer_hand])
        player_value = self.calculate_hand_value([card[:-1] for card in player_hand])

        # Function to display the game state
        def create_embed():
            embed = discord.Embed(title="🎲 Blackjack Game", color=discord.Color.blurple())
            embed.add_field(name="Dealer's Hand", value=f"{dealer_hand[0]} ❓", inline=False)
            embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=False)
            embed.add_field(name="Your Bet", value=f"${bet}", inline=True)
            embed.add_field(name="Your Balance", value=f"${balance}", inline=True)
            return embed

        # Create buttons for the game
        view = discord.ui.View()

        async def hit_callback(interaction):
            """Handle the Hit button."""
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("This is not your game!", ephemeral=True)
                return

            # Player draws a card
            player_hand.append(self.draw_card())
            player_value = self.calculate_hand_value([card[:-1] for card in player_hand])

            if player_value > 21:
                # Player busts
                result_embed = discord.Embed(title="💥 You Bust!", color=discord.Color.red())
                result_embed.add_field(name="Dealer's Hand", value=f"{' '.join(dealer_hand)} ({dealer_value})", inline=False)
                result_embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=False)
                result_embed.add_field(name="Result", value="You lose!", inline=False)
                self.update_user_balance(user_id, -bet)
                result_embed.add_field(name="New Balance", value=f"${self.get_user_balance(user_id)}", inline=True)

                await interaction.response.edit_message(embed=result_embed, view=None)
            else:
                # Update game state
                await interaction.response.edit_message(embed=create_embed(), view=view)

        async def stand_callback(interaction):
            """Handle the Stand button."""
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("This is not your game!", ephemeral=True)
                return

            # Dealer's turn
            while dealer_value < 17:
                dealer_hand.append(self.draw_card())
                dealer_value = self.calculate_hand_value([card[:-1] for card in dealer_hand])

            # Determine the result
            if dealer_value > 21 or player_value > dealer_value:
                result = "You win!"
                winnings = bet
            elif player_value == dealer_value:
                result = "It's a tie!"
                winnings = 0
            else:
                result = "You lose!"
                winnings = -bet

            # Update balance
            self.update_user_balance(user_id, winnings)

            # Show final result
            result_embed = discord.Embed(title="🎲 Blackjack Result", color=discord.Color.green() if winnings > 0 else discord.Color.red())
            result_embed.add_field(name="Dealer's Hand", value=f"{' '.join(dealer_hand)} ({dealer_value})", inline=False)
            result_embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=False)
            result_embed.add_field(name="Result", value=result, inline=False)
            result_embed.add_field(name="Winnings", value=f"${winnings}", inline=True)
            result_embed.add_field(name="New Balance", value=f"${self.get_user_balance(user_id)}", inline=False)

            await interaction.response.edit_message(embed=result_embed, view=None)

        # Add buttons to the view
        hit_button = discord.ui.Button(label="Hit", style=discord.ButtonStyle.green)
        stand_button = discord.ui.Button(label="Stand", style=discord.ButtonStyle.red)

        hit_button.callback = hit_callback
        stand_button.callback = stand_callback

        view.add_item(hit_button)
        view.add_item(stand_button)

        # Send the initial game state
        await ctx.respond(embed=create_embed(), view=view)

def setup(bot):
    bot.add_cog(Blackjack(bot))
