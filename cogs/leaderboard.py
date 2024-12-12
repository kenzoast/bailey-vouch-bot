import discord
from discord.ext import commands
import sqlite3

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "fishing_game.db"  

    @discord.app_commands.command(name="leaderboard", description="View the top players and their balances.")
    async def leaderboard(self, interaction: discord.Interaction):
        """Displays the leaderboard of the top users and their balances."""
        
        try:

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()


            c.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
            top_users = c.fetchall()
            conn.close()

            if not top_users:
                await interaction.response.send_message("❌ No users found in the leaderboard.", ephemeral=True)
                return

            embed = discord.Embed(
                title="🏆 **Leaderboard** 🏆",
                description="Top players and their balances.",
                color=discord.Color.gold()
            )


            for i, (user_id, balance) in enumerate(top_users, start=1):
                user = self.bot.get_user(int(user_id))  
                user_display_name = user.display_name if user else f"Unknown User ({user_id})"

                embed.add_field(
                    name=f"#{i} - {user_display_name}",
                    value=f"💰 **${balance:,.2f}**",
                    inline=False
                )

            if len(top_users) > 10:
                embed.set_footer(text="Only the top 10 users are displayed.")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
