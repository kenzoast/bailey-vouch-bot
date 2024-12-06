import discord
from discord.ext import commands
import random
import sqlite3

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("balance.db")
        self.cursor = self.db.cursor()
        self.setup_database()

    def setup_database(self):
        """Create the balance table if it doesn't exist."""
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 100)")
            self.db.commit()
            print("Database initialized successfully!")
        except sqlite3.Error as e:
            print(f"Database setup error: {e}")

    def get_user_balance(self, user_id):
        """Get the user's balance from the database."""
        try:
            self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                self.cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 100))
                self.db.commit()
                return 100
        except sqlite3.Error as e:
            print(f"Error retrieving balance: {e}")
            return 0

    def update_user_balance(self, user_id, amount):
        """Update the user's balance in the database."""
        try:
            balance = self.get_user_balance(user_id)
            new_balance = balance + amount
            self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            self.db.commit()
        except sqlite3.Error as e:
            print(f"Error updating balance: {e}")

    def draw_card(self):
        """Draw a card for the game."""
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        return f"{random.choice(ranks)}{random.choice(suits)}"

    def calculate_hand_value(self, hand):
        """Calculate the total value of a hand."""
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
        total = 0
        aces = 0

        for card in hand:
            rank = card[:-1]  # Remove the suit
            total += values[rank]
            if rank == 'A':
                aces += 1

        # Adjust for Aces if the total is over 21
        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    @commands.slash_command(name="blackjack", description="Play a game of blackjack.")
    async def blackjack(self, ctx, bet: int):
        try:
            user_id = ctx.author.id
            balance = self.get_user_balance(user_id)

            if bet <= 0:
                await ctx.respond("Bet must be greater than 0.", ephemeral=True)
                return
            if bet > balance:
                await ctx.respond("You don't have enough balance to place that bet.", ephemeral=True)
                return

            # Initialize game state
            dealer_hand = [self.draw_card(), self.draw_card()]
            player_hand = [self.draw_card(), self.draw_card()]
            player_value = self.calculate_hand_value([card[:-1] for card in player_hand])
            dealer_value = self.calculate_hand_value([card[:-1] for card in dealer_hand])

            # Function to display the game state
            def create_embed():
                nonlocal player_value  # Ensure player_value updates dynamically
                player_value = self.calculate_hand_value([card[:-1] for card in player_hand])
                embed = discord.Embed(title="🎲 Blackjack Game", color=discord.Color.blurple())
                embed.add_field(name="Dealer's Hand", value=f"{dealer_hand[0]} ❓", inline=False)
                embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=False)
                embed.add_field(name="Your Bet", value=f"${bet}", inline=True)
                embed.add_field(name="Your Balance", value=f"${balance}", inline=True)
                return embed

            # Create interactive buttons
            view = discord.ui.View()

            async def hit_callback(interaction):
                """Handle the Hit button."""
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("This is not your game!", ephemeral=True)
                    return

                # Player draws a card
                player_hand.append(self.draw_card())
                player_value = self.calculate_hand_value([card[:-1] for card in player_hand])  # Update value

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

                # Determine result
                result_embed = discord.Embed(title="🎲 Blackjack Result", color=discord.Color.blurple())
                result_embed.add_field(name="Dealer's Hand", value=f"{' '.join(dealer_hand)} ({dealer_value})", inline=False)
                result_embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=False)

                if dealer_value > 21 or player_value > dealer_value:
                    result_embed.add_field(name="Result", value="You win!", inline=False)
                    self.update_user_balance(user_id, bet)
                elif player_value == dealer_value:
                    result_embed.add_field(name="Result", value="It's a tie!", inline=False)
                else:
                    result_embed.add_field(name="Result", value="You lose!", inline=False)
                    self.update_user_balance(user_id, -bet)

                result_embed.add_field(name="New Balance", value=f"${self.get_user_balance(user_id)}", inline=True)
                await interaction.response.edit_message(embed=result_embed, view=None)

            hit_button = discord.ui.Button(label="Hit", style=discord.ButtonStyle.green)
            hit_button.callback = hit_callback

            stand_button = discord.ui.Button(label="Stand", style=discord.ButtonStyle.red)
            stand_button.callback = stand_callback

            view.add_item(hit_button)
            view.add_item(stand_button)

            # Send the initial game state
            await ctx.respond(embed=create_embed(), view=view)
        except Exception as e:
            print(f"Error in blackjack command: {e}")

def setup(bot):
    bot.add_cog(Blackjack(bot))
