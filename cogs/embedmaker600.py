import discord
from discord import Embed, Member, ApplicationContext
from discord.ext import commands
from discord.ui import Button, View
from discord.ext.commands import has_permissions

class EmbedMaker600View(View):
    """This view contains buttons to customize the embed."""
    def __init__(self):
        super().__init__(timeout=None)  # View doesn't timeout automatically

        # Create buttons for each action
        self.add_item(Button(label="Add Field", custom_id="add_field", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Add Image", custom_id="add_image", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Add Thumbnail", custom_id="add_thumbnail", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Add Footer", custom_id="add_footer", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Add Author", custom_id="add_author", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Add Title", custom_id="add_title", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Add Description", custom_id="add_description", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Add Color", custom_id="add_color", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Send", custom_id="send", style=discord.ButtonStyle.danger))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command user can interact with the buttons."""
        return True  # You can change this to `return interaction.user == <some_user>`

class EmbedMaker600(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="embed_maker", description="Create a custom embed message")  # Removed the space in the command name
    @has_permissions(manage_messages=True)
    async def embed_maker(self, ctx: ApplicationContext):
        """Command to start the embed builder."""
        
        embed = Embed(
            title="Embed Maker",
            description="Use the buttons below to customize your embed message",
            color=discord.Color.blue()
        )
        
        view = EmbedMaker600View()
        
        # Send the embed message with the buttons
        await ctx.respond(embed=embed, view=view, ephemeral=True)  # Changed to ephemeral=True so only the user sees it

async def setup(bot):
    await bot.add_cog(EmbedMaker600(bot))
