import discord
from utils import database
from wrappers.embedWrapper import create_embed
import asyncio

class EmbedEditView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id

    @discord.ui.button(label="Edit Title", style=discord.ButtonStyle.primary)
    async def edit_title(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Please enter the new embed title (you can use variables like {user}):", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            new_title = msg.content
            # Save the new title to the database
            database.set_embed_setting(self.guild_id, 'title', new_title)
            success_embed = create_embed(
                title="Title Updated",
                description=f"The embed title has been updated to: {new_title}",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=success_embed, ephemeral=True)
            await msg.delete()
        except asyncio.TimeoutError:
            timeout_embed = create_embed(
                title="Timed Out",
                description="You took too long to respond. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)

    @discord.ui.button(label="Edit Description", style=discord.ButtonStyle.primary)
    async def edit_description(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Please enter the new embed description (you can use variables like {message}):", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            new_description = msg.content
            # Save the new description to the database
            database.set_embed_setting(self.guild_id, 'description', new_description)
            success_embed = create_embed(
                title="Description Updated",
                description="The embed description has been updated.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=success_embed, ephemeral=True)
            await msg.delete()
        except asyncio.TimeoutError:
            timeout_embed = create_embed(
                title="Timed Out",
                description="You took too long to respond. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)

    @discord.ui.button(label="Edit Color", style=discord.ButtonStyle.primary)
    async def edit_color(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Please enter the new embed color in hex format (e.g., #3498db):", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            new_color = msg.content
            if not new_color.startswith('#') or len(new_color) != 7:
                error_embed = create_embed(
                    title="Invalid Color",
                    description="Please provide a valid hex color code, e.g., #3498db.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            else:
                # Save the new color to the database
                database.set_embed_setting(self.guild_id, 'color', new_color)
                success_embed = create_embed(
                    title="Color Updated",
                    description=f"The embed color has been updated to {new_color}.",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=success_embed, ephemeral=True)
            await msg.delete()
        except asyncio.TimeoutError:
            timeout_embed = create_embed(
                title="Timed Out",
                description="You took too long to respond. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)


    # Optional: If you want an in-app Docs button
    @discord.ui.button(label="Variables", style=discord.ButtonStyle.secondary)
    async def variables_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        variables = """
**Available Variables:**
- `{user}`: The user being vouched for.
- `{voucher}`: The user who is giving the vouch.
- `{message}`: The vouch message.
- `{stars}`: The star rating.
- `{vouch_count}`: The total number of vouches for the user.
"""
        embed = create_embed(
            title="Embed Variables",
            description=variables,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
