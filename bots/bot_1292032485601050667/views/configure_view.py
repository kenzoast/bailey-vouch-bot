import discord
from utils import database
import asyncio
from wrappers.embedWrapper import create_embed
from views.embed_edit_view import EmbedEditView

class ConfigureView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    # Button to set the vouch channel
    @discord.ui.button(label="Set Vouch Channel", style=discord.ButtonStyle.primary)
    async def set_vouch_channel(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Set Vouch Channel",
            description="Please mention the channel you want to set as the vouch channel.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            # Wait for the user to mention a channel
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            if msg.channel_mentions:
                channel = msg.channel_mentions[0]
                # Save the vouch channel to the database
                database.set_vouch_channel(interaction.guild.id, channel.id)
                success_embed = discord.Embed(
                    title="Vouch Channel Set",
                    description=f"Vouch channel has been set to {channel.mention}.",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=success_embed, ephemeral=True)
            else:
                error_embed = discord.Embed(
                    title="No Channel Mentioned",
                    description="No channel mentioned. Please try again.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            # Delete the user's message
            await msg.delete()
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="Timed Out",
                description="You took too long to respond. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)


                # Button to set the vouch role
    @discord.ui.button(label="Set Vouch Role", style=discord.ButtonStyle.primary)
    async def set_vouch_role(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = create_embed(
            title="Set Vouch Role",
            description="Please mention the role you want to set as the required role for the /vouch command.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            if msg.role_mentions:
                role = msg.role_mentions[0]
                # Save the vouch role to the database
                database.set_vouch_role(interaction.guild.id, role.id)
                success_embed = create_embed(
                    title="Vouch Role Set",
                    description=f"The required role for /vouch command has been set to {role.mention}.",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=success_embed, ephemeral=True)
            else:
                error_embed = create_embed(
                    title="No Role Mentioned",
                    description="No role mentioned. Please try again.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            # Delete the user's message
            await msg.delete()
        except asyncio.TimeoutError:
            timeout_embed = create_embed(
                title="Timed Out",
                description="You took too long to respond. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)

        # Button to edit the embed
    @discord.ui.button(label="Edit Embed", style=discord.ButtonStyle.secondary)
    async def edit_embed(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = create_embed(
            title="Edit Embed",
            description="Use the buttons below to edit the embed template for vouches.",
            color=discord.Color.blue()
        )
        view = EmbedEditView(self.bot, interaction.guild.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


