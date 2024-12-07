import discord
from discord.ext import commands
import random
import sqlite3

# Ensure the SQLite database is connected
DB_PATH = "fishing_game.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

class Gamble(commands.Cog):
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

    @commands.slash_command(name="gamble", description="Choose a gambling game and bet money!")
    async def gamble(self, ctx, bet: int):
        """
        Provide users with a choice to gamble using Coinflip, Dice Roll, Blackjack, or Slots, with a betting system.
        """
        user_id = ctx.author.id
        balance = self.get_user_balance(user_id)

        # Ensure the user has enough balance
        if bet <= 0:
            await ctx.respond("Your bet must be greater than $0.", ephemeral=True)
            return
        if bet > balance:
            await ctx.respond("You don't have enough balance to place this bet.", ephemeral=True)
            return

        # Create a selection menu for gambling games
        class GamblingView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

                # Add buttons for each gambling game
                self.add_item(discord.ui.Button(label="Coinflip", style=discord.ButtonStyle.primary, custom_id="coinflip"))
                self.add_item(discord.ui.Button(label="Roll a Dice", style=discord.ButtonStyle.secondary, custom_id="roll_dice"))
                self.add_item(discord.ui.Button(label="Blackjack", style=discord.ButtonStyle.success, custom_id="blackjack"))
                self.add_item(discord.ui.Button(label="Slots", style=discord.ButtonStyle.danger, custom_id="slots"))

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user.id == ctx.author.id

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True

        # Send initial embed and buttons
        embed = discord.Embed(
            title="🎲 Gamble Options",
            description=f"Choose a game to play with your bet of **${bet}**:\n- **Coinflip**\n- **Roll a Dice**\n- **Blackjack**\n- **Slots**",
            color=discord.Color.blue()
        )
        view = GamblingView()
        await ctx.respond(embed=embed, view=view)

        # Wait for user interaction
        interaction = await self.bot.wait_for("interaction", check=lambda i: i.custom_id in ["coinflip", "roll_dice", "blackjack", "slots"] and i.user.id == ctx.author.id)

        if interaction.custom_id == "coinflip":
            await self.coinflip(ctx, bet)
        elif interaction.custom_id == "roll_dice":
            await self.roll_dice(ctx, bet)
        elif interaction.custom_id == "blackjack":
            await ctx.send("Use `/blackjack` to play the game.")
        elif interaction.custom_id == "slots":
            await self.slots(ctx, bet)

    async def coinflip(self, ctx, bet):
        """Simulates a coin flip with a bet."""
        result = random.choice(["Heads", "Tails"])
        outcome = random.choice(["win", "lose"])

        if outcome == "win":
            self.update_user_balance(ctx.author.id, bet)
            description = f"The coin landed on **{result}**! You won **${bet}**!"
            color = discord.Color.green()
        else:
            self.update_user_balance(ctx.author.id, -bet)
            description = f"The coin landed on **{result}**! You lost **${bet}**!"
            color = discord.Color.red()

        embed = discord.Embed(
            title="Coin Flip",
            description=description,
            color=color
        )
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(ctx.author.id)}", inline=False)
        await ctx.send(embed=embed)

    async def roll_dice(self, ctx, bet):
        """Simulates rolling a dice with a bet."""
        player_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if player_roll > bot_roll:
            self.update_user_balance(ctx.author.id, bet)
            description = f"You rolled **{player_roll}**. The bot rolled **{bot_roll}**. You won **${bet}**!"
            color = discord.Color.green()
        elif player_roll < bot_roll:
            self.update_user_balance(ctx.author.id, -bet)
            description = f"You rolled **{player_roll}**. The bot rolled **{bot_roll}**. You lost **${bet}**!"
            color = discord.Color.red()
        else:
            description = f"You rolled **{player_roll}**. The bot rolled **{bot_roll}**. It's a tie!"
            color = discord.Color.blue()

        embed = discord.Embed(
            title="Dice Roll",
            description=description,
            color=color
        )
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(ctx.author.id)}", inline=False)
        await ctx.send(embed=embed)

    async def slots(self, ctx, bet):
        """Simulates a slot machine spin with a bet."""
        symbols = ["🍒", "🍋", "🔔", "⭐", "💎"]
        slot_result = [random.choice(symbols) for _ in range(3)]

        if len(set(slot_result)) == 1:
            winnings = bet * 5
            self.update_user_balance(ctx.author.id, winnings)
            outcome = f"🎉 JACKPOT! You won **${winnings}**!"
            color = discord.Color.gold()
        elif len(set(slot_result)) == 2:
            winnings = bet * 2
            self.update_user_balance(ctx.author.id, winnings)
            outcome = f"👏 Close! You won **${winnings}**!"
            color = discord.Color.blue()
        else:
            self.update_user_balance(ctx.author.id, -bet)
            outcome = f"😢 Better luck next time! You lost **${bet}**."
            color = discord.Color.red()

        embed = discord.Embed(
            title="🎰 Slots Machine",
            description=f"Result: {' '.join(slot_result)}\n\n{outcome}",
            color=color
        )
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(ctx.author.id)}", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Gamble(bot))
