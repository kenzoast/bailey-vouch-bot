import discord
from discord.ext import commands
from discord.ui import View, Button


class SkibidiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # List of allowed Discord IDs
        self.sigma_ids = [
            1264623647671451679, 450331258094878730, 761654350086799410,
            1155798723515920404, 1280152659134775299, 571951965500735498,
            1292032485601050667, 881599312449118209, 1242588844688408681,
            1169382966535925902, 1288177542750142658, 1235525090108641311
        ]  # Replace with your desired IDs

    @discord.slash_command(name="skibidi", description="Check if you're sigma or check another user.")
    async def skibidi(self, ctx: discord.ApplicationContext, user: discord.Member = None):
        # Determine the user to check (default to the command author)
        target_user = user or ctx.author

        if target_user.id in self.sigma_ids:
            current_index = self.sigma_ids.index(target_user.id)

            # Create the embed
            embed = discord.Embed(
                title="Sigma Alert",
                color=discord.Color.green()
            )
            embed.add_field(name="User", value=f"{target_user}", inline=True)
            embed.add_field(name="User ID", value=f"{target_user.id}", inline=True)
            embed.add_field(name="Sigma", value="True", inline=False)
            embed.set_footer(text="Use the arrows to view other sigma users.")
            
            # Create the navigation view
            view = SigmaNavigationView(self.sigma_ids, current_index, ctx)
            await ctx.respond(embed=embed, view=view, ephemeral=True)
        else:
            await ctx.respond("You're not sigma...", ephemeral=True)


class SigmaNavigationView(View):
    def __init__(self, sigma_ids, current_index, ctx):
        super().__init__()
        self.sigma_ids = sigma_ids
        self.current_index = current_index
        self.ctx = ctx
        self.update_buttons()

    async def update_embed(self, interaction):
        # Fetch the current user based on the index
        current_user_id = self.sigma_ids[self.current_index]
        current_user = self.ctx.guild.get_member(current_user_id)
        
        if current_user:
            embed = discord.Embed(
                title="Sigma Alert",
                color=discord.Color.green()
            )
            embed.add_field(name="User", value=f"{current_user}", inline=True)
            embed.add_field(name="User ID", value=f"{current_user.id}", inline=True)
            embed.add_field(name="Sigma", value="True", inline=False)
            embed.set_footer(text="This command was suggested by connor.")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("User not found.", ephemeral=True)

    def update_buttons(self):
        # Disable the buttons if we are at the start or end of the list
        self.clear_items()
        self.add_item(Button(label="⬅️", style=discord.ButtonStyle.secondary, custom_id="prev", disabled=self.current_index <= 0))
        self.add_item(Button(label="➡️", style=discord.ButtonStyle.secondary, custom_id="next", disabled=self.current_index >= len(self.sigma_ids) - 1))

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, button: Button, interaction: discord.Interaction):
        self.current_index -= 1
        self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, button: Button, interaction: discord.Interaction):
        self.current_index += 1
        self.update_buttons()
        await self.update_embed(interaction)


# Setup function to add the cog
def setup(bot):
    bot.add_cog(SkibidiCog(bot))
