import discord
from discord.ext import commands
from discord import app_commands  # Ensure this import is correct

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
        
        # Default color if none is provided
        embed_color = 0x3498DB  # Default color (blue)
        
        if color:
            try:
                embed_color = int(color.replace("#", ""), 16)
            except ValueError:
                await interaction.response.send_message(
                    "❌ **Invalid color format.** Use a hex code like **#FF5733**.", 
                    ephemeral=True
                )
                return
        
        # Create the embed
        embed = discord.Embed(
            title=title if title else "📢 **No Title Provided**",
            description=description if description else "📝 **No Description Provided**",
            color=embed_color
        )

        if footer:
            embed.set_footer(text=footer)
        
        if thumbnail:
            if self.valid_image_url(thumbnail):
                embed.set_thumbnail(url=thumbnail)
            else:
                await interaction.response.send_message(
                    "❌ **Invalid URL for the thumbnail.** Please provide a valid image URL.", 
                    ephemeral=True
                )
                return

        if image:
            if self.valid_image_url(image):
                embed.set_image(url=image)
            else:
                await interaction.response.send_message(
                    "❌ **Invalid URL for the image.** Please provide a valid image URL.", 
                    ephemeral=True
                )
                return
        
        try:
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                f"❌ **Error creating the embed:** {e}", 
                ephemeral=True
            )

    def valid_image_url(self, url: str) -> bool:
        """Basic validation for an image URL (checks if URL ends with an image file extension)."""
        valid_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
        return url.startswith("http") and any(url.lower().endswith(ext) for ext in valid_extensions)

async def setup(bot):
    await bot.add_cog(EmbedBuilder(bot))
