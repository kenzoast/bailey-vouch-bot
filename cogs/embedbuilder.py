import discord
from discord import app_commands
from discord.ext import commands

class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Create a custom embed message")
    @app_commands.describe(
        title="The title of the embed",
        description="The description of the embed",
        color="The hex color for the embed (e.g., #FF5733 or #FFFFFF)",
        footer="The footer of the embed",
        thumbnail="The URL of the thumbnail image",
        image="The URL of the main image"
    )
    async def embed(
        self, 
        interaction: discord.Interaction, 
        title: str = None, 
        description: str = None, 
        color: str = None, 
        footer: str = None, 
        thumbnail: str = None, 
        image: str = None
    ):
        """Creates a custom embed with various options."""
        
        # Default color if none provided
        embed_color = 0x3498DB  # Default color (blue) if no color is provided
        
        if color:
            try:
                embed_color = int(color.replace("#", ""), 16)
            except ValueError:
                await interaction.response.send_message("❌ Invalid color format. Use a hex code like **#FF5733**.", ephemeral=True)
                return
        
        # Create the embed
        embed = discord.Embed(
            title=title if title else "No Title Provided",
            description=description if description else "No Description Provided",
            color=embed_color
        )

        if footer:
            embed.set_footer(text=footer)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if image:
            embed.set_image(url=image)
        
        try:
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating the embed: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmbedBuilder(bot))
