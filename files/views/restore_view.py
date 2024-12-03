import discord
from wrappers.embedWrapper import create_embed

class RestoreView(discord.ui.View):
    def __init__(self, bot, vouches):
        super().__init__(timeout=180)
        self.bot = bot
        self.vouches = vouches
        self.current_page = 0
        self.vouches_per_page = 5
        self.total_pages = (len(vouches) - 1) // self.vouches_per_page + 1

    def get_current_embed(self):
        start = self.current_page * self.vouches_per_page
        end = start + self.vouches_per_page
        embed = create_embed(
            title=f"All Vouches (Page {self.current_page + 1}/{self.total_pages})",
            color=discord.Color.blue()
        )
        for vouch in self.vouches[start:end]:
            user = f"<@{vouch['user_id']}>"
            voucher = f"<@{vouch['voucher_id']}>"
            stars = "⭐" * vouch['stars']
            message = vouch['message']
            embed.add_field(
                name=f"{stars} | {user} vouched by {voucher}",
                value=message,
                inline=False
            )
        return embed

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.primary)
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            embed = self.get_current_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='Next', style=discord.ButtonStyle.primary)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            embed = self.get_current_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        # Optionally, you can edit the message to disable buttons
        # message = self.message
        # await message.edit(view=self)
