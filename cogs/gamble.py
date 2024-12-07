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
        Provide users with a choice to gamble using Coinflip, Dice Roll, Slots, or HighLow, with a betting system.
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
                self.add_item(discord.ui.Button(label="Coinflip", style=discord.ButtonStyle.primary, custom_id="coinflip"))
                self.add_item(discord.ui.Button(label="Roll a Dice", style=discord.ButtonStyle.secondary, custom_id="roll_dice"))
                self.add_item(discord.ui.Button(label="Slots", style=discord.ButtonStyle.danger, custom_id="slots"))
                self.add_item(discord.ui.Button(label="HighLow", style=discord.ButtonStyle.success, custom_id="highlow"))

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user.id == ctx.author.id

        # Send initial embed and buttons
        embed = discord.Embed(
            title="🎲 Gamble Options",
            description=f"Choose a game to play with your bet of **${bet}**:\n- **Coinflip**\n- **Roll a Dice**\n- **Slots**\n- **HighLow**",
            color=discord.Color.blue()
        )
        view = GamblingView()
        await ctx.respond(embed=embed, view=view)

        # Wait for user interaction
        interaction = await self.bot.wait_for(
            "interaction",
            check=lambda i: i.custom_id in ["coinflip", "roll_dice", "slots", "highlow"] and i.user.id == ctx.author.id
        )

        if interaction.custom_id == "coinflip":
            await self.coinflip(ctx, bet)
        elif interaction.custom_id == "roll_dice":
            await self.roll_dice(ctx, bet)
        elif interaction.custom_id == "slots":
            await self.slots(ctx, bet)
        elif interaction.custom_id == "highlow":
            await self.highlow(ctx, bet)

    async def roll_dice(self, ctx, bet):
        """Roll a dice and calculate results based on a threshold."""
        roll = random.randint(1, 100)
        win = roll >= 50  # Win if the roll is 50 or higher

        if win:
            winnings = bet * 2  # Double the bet on a win
            self.update_user_balance(ctx.author.id, winnings)
            description = f"You rolled a **{roll}** and won **${winnings}**!"
            color = discord.Color.green()
        else:
            self.update_user_balance(ctx.author.id, -bet)
            description = f"You rolled a **{roll}** and lost your bet of **${bet}**."
            color = discord.Color.red()

        embed = discord.Embed(
            title="🎲 Dice Roll Result",
            description=description,
            color=color
        )
        embed.add_field(name="New Balance", value=f"${self.get_user_balance(ctx.author.id)}", inline=False)
        await ctx.respond(embed=embed)

    async def highlow(self, ctx, bet):
        """HighLow game with rewards based on probabilities."""
        cards = list(range(2, 15))  # Cards from 2 to Ace (14)
        current_card = random.choice(cards)
        streak = 0
        total_winnings = 0

        async def play_round(interaction, guess):
            nonlocal current_card, streak, total_winnings
            next_card = random.choice(cards)

            higher_prob = len([c for c in cards if c > current_card]) / len(cards)
            lower_prob = len([c for c in cards if c < current_card]) / len(cards)

            correct_guess = (guess == "higher" and next_card > current_card) or (guess == "lower" and next_card < current_card)

            if correct_guess:
                streak += 1
                reward = int(bet * (1 / higher_prob if guess == "higher" else 1 / lower_prob))
                total_winnings += reward
                current_card = next_card

                embed = discord.Embed(
                    title="🎴 HighLow Game",
                    description=f"Correct! The next card was **{next_card}**.\nCurrent Streak: **{streak}**.\nTotal Winnings: **${total_winnings}**.",
                    color=discord.Color.green()
                )
                embed.add_field(name="Current Card", value=f"**{current_card}**")
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                self.update_user_balance(ctx.author.id, -bet)
                embed = discord.Embed(
                    title="🎴 HighLow Game",
                    description=f"Wrong! The next card was **{next_card}**.\nYou lost your bet of **${bet}**.",
                    color=discord.Color.red()
                )
                embed.add_field(name="New Balance", value=f"${self.get_user_balance(ctx.author.id)}", inline=False)
                await interaction.response.edit_message(embed=embed, view=None)

        async def cash_out(interaction):
            self.update_user_balance(ctx.author.id, total_winnings)
            embed = discord.Embed(
                title="🎴 HighLow - Cash Out",
                description=f"You cashed out with a total of **${total_winnings}**!",
                color=discord.Color.gold()
            )
            embed.add_field(name="New Balance", value=f"${self.get_user_balance(ctx.author.id)}", inline=False)
            await interaction.response.edit_message(embed=embed, view=None)

        embed = discord.Embed(
            title="🎴 HighLow Game",
            description=f"The current card is **{current_card}**.\nWill the next card be higher or lower?",
            color=discord.Color.blue()
        )
        view = discord.ui.View(timeout=60)
        view.add_item(discord.ui.Button(label="Higher", style=discord.ButtonStyle.success, custom_id="higher", callback=lambda i: play_round(i, "higher")))
        view.add_item(discord.ui.Button(label="Lower", style=discord.ButtonStyle.danger, custom_id="lower", callback=lambda i: play_round(i, "lower")))
        view.add_item(discord.ui.Button(label="Cash Out", style=discord.ButtonStyle.primary, callback=cash_out))
        await ctx.respond(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Gamble(bot))
