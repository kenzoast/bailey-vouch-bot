import discord
from discord import Embed, Member, ApplicationContext
from discord.ext import commands
from discord.ui import Button, View
from discord.ext.commands import has_permissions

class EmbedMaker600(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="embed maker", description="Create a custom embed message")
    @has_permissions(manage_messages=True)
    async def embed_maker(self, ctx: ApplicationContext):
        embed = Embed(title="Embed Maker", description="Use the buttons below to customize your embed message")
        
        # Create the view object
        view = View()
        
        # Create the buttons
        button1 = Button(label="Add Field", custom_id="add_field", style=1)
        button2 = Button(label="Add Image", custom_id="add_image", style=1)
        button3 = Button(label="Add Thumbnail", custom_id="add_thumbnail", style=1)
        button4 = Button(label="Add Footer", custom_id="add_footer", style=1)
        button5 = Button(label="Add Author", custom_id="add_author", style=1)
        button6 = Button(label="Add Title", custom_id="add_title", style=1)
        button7 = Button(label="Add Description", custom_id="add_description", style=1)
        button8 = Button(label="Add Color", custom_id="add_color", style=1)
        button9 = Button(label="Send", custom_id="send", style=4)
        
        # Add the buttons to the view
        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)
        view.add_item(button5)
        view.add_item(button6)
        view.add_item(button7)
        view.add_item(button8)
        view.add_item(button9)
        
        # Send the embed message
        await ctx.send(embed=embed, view=view)
