import discord
from discord.ext import commands
import sqlite3

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "fishing_game.db"  # Update this if your DB is in a different location

    @commands.command(name="leaderboard", description="View the top players and their balances.")
    async def leaderboard(self, ctx):
        """Displays the leaderboard of the top users and their balances."""
        
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Query the top 10 users sorted by balance
            c.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
            top_users = c.fetchall()
            conn.close()

            if not top_users:
                await ctx.send("❌ No users found in the leaderboard.")
                return

            # Create an embed to display the leaderboard
            embed = discord.Embed(
                title="🏆 **Leaderboard** 🏆",
                description="Top players and their balances.",
                color=discord.Color.gold()
            )

            # Display top 10 users
            for i, (user_id, balance) in enumerate(top_users, start=1):
                user = await self.bot.fetch_user(user_id)  # Uses fetch_user to get the user object
                user_display_name = user.name if user else f"Unknown User ({user_id})"

                embed.add_field(
                    name=f"#{i} - {user_display_name}",
                    value=f"💰 **${balance:,.2f}**",
                    inline=False
                )

            if len(top_users) > 10:
                embed.set_footer(text="Only the top 10 users are displayed.")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
