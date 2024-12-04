import discord
from discord.ext import commands
import sqlite3


class TicketPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("tickets.db")
        self.cursor = self.db.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                user_id INTEGER
            )
        """)
        self.db.commit()
        self.ticket_category_id = 1312813869030178852  # Replace with your category ID

    @commands.slash_command()
    async def ticket_panel(self, ctx: discord.ApplicationContext):
        """Creates a ticket panel with buttons."""
        embed = discord.Embed(
            title="Ticket Panel",
            description="Choose an option below to get started.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="🎫 Support Ticket", value="Create a private support channel.", inline=False)
        embed.add_field(name="👮 Staff Application", value="Apply to become a staff member.", inline=False)
        embed.add_field(name="⭐ Purchase Premium", value="Upgrade to premium for exclusive benefits.", inline=False)
        embed.set_footer(text="Click a button below to proceed.")

        view = TicketPanelView(self.bot, self.db, self.ticket_category_id)
        await ctx.respond("Sent Ticket Panel.")
        await ctx.channel.send(embed=embed, view=view)

    @commands.slash_command()
    async def ticket_close(self, ctx: discord.ApplicationContext):
        """Closes the ticket channel."""
        if isinstance(ctx.channel, discord.TextChannel):
            self.cursor.execute("SELECT * FROM tickets WHERE channel_id = ?", (ctx.channel.id,))
            ticket = self.cursor.fetchone()
            if ticket:
                view = ConfirmCloseView(self.db, ctx.channel)
                await ctx.respond("Are you sure you want to close this ticket?", view=view, ephemeral=True)
                return
        await ctx.respond("This is not a valid ticket channel.", ephemeral=True)

    @commands.slash_command()
    async def ticket_add(self, ctx: discord.ApplicationContext, member: discord.Member):
        """Adds a user to the ticket channel."""
        if isinstance(ctx.channel, discord.TextChannel):
            self.cursor.execute("SELECT * FROM tickets WHERE channel_id = ?", (ctx.channel.id,))
            ticket = self.cursor.fetchone()
            if ticket:
                await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
                await ctx.respond(f"{member.mention} has been added to the ticket.")
                return
        await ctx.respond("This is not a valid ticket channel.", ephemeral=True)


class TicketPanelView(discord.ui.View):
    def __init__(self, bot, db, category_id):
        super().__init__(timeout=None)  # Persistent views require no timeout
        self.bot = bot
        self.db = db
        self.category_id = category_id

    @discord.ui.button(label="Support Ticket", style=discord.ButtonStyle.gray, emoji="🎫", custom_id="ticket_support")
    async def support_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        # Check if the user already has a ticket
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM tickets WHERE user_id = ?", (user.id,))
        if cursor.fetchone():
            embed = discord.Embed(
                title="Ticket Exists",
                description="You already have an open ticket.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get the category
        category = guild.get_channel(self.category_id)
        if category is None or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Ticket category is not configured correctly.", ephemeral=True)
            return

        # Create a private channel for the ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        channel = await category.create_text_channel(name=f"ticket-{user.name}", overwrites=overwrites)
        cursor.execute("INSERT INTO tickets (channel_id, user_id) VALUES (?, ?)", (channel.id, user.id))
        self.db.commit()

        # Send an embed in the ticket channel with a close button
        embed = discord.Embed(
            title="Support Ticket",
            description="Please describe your issue in detail. A staff member will assist you shortly.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="User ID", value=user.id)
        embed.set_footer(text="Ticket System")
        view = CloseTicketView(self.db)
        await channel.send(embed=embed, view=view)

        # Send a notification to the user
        notify_embed = discord.Embed(
            title="Ticket Created",
            description=f"Your ticket has been created: {channel.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=notify_embed, ephemeral=True)

    @discord.ui.button(label="Staff Application", style=discord.ButtonStyle.green, emoji="👮", custom_id="staff_application")
    async def staff_application(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Staff Application",
            description="Apply to become a staff member by clicking the button below.",
            color=discord.Color.green()
        )
        view = LinkButtonView(label="Apply Now", url="https://forms.gle/vFsjrELj3vszyLrSA")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Purchase Premium", style=discord.ButtonStyle.blurple, emoji="⭐", custom_id="purchase_premium")
    async def purchase_premium(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Purchase Premium",
            description="Upgrade to premium for exclusive benefits by clicking the button below.",
            color=discord.Color.blue()
        )
        view = LinkButtonView(label="Purchase Premium", url="https://bailey.sellauth.com/")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)



class CloseTicketView(discord.ui.View):
    def __init__(self, db):
        super().__init__()
        self.db = db

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = interaction.channel
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM tickets WHERE channel_id = ?", (channel.id,))
        ticket = cursor.fetchone()
        if ticket:
            view = ConfirmCloseView(self.db, channel)
            await interaction.response.send_message("Are you sure you want to close this ticket?", view=view, ephemeral=True)
        else:
            await interaction.response.send_message("This is not a valid ticket channel.", ephemeral=True)


class ConfirmCloseView(discord.ui.View):
    def __init__(self, db, channel):
        super().__init__()
        self.db = db
        self.channel = channel

    @discord.ui.button(label="Yes, close the ticket", style=discord.ButtonStyle.red)
    async def confirm_close(self, button: discord.ui.Button, interaction: discord.Interaction):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tickets WHERE channel_id = ?", (self.channel.id,))
        self.db.commit()
        await self.channel.delete()

    @discord.ui.button(label="No, keep the ticket", style=discord.ButtonStyle.gray)
    async def cancel_close(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)


class LinkButtonView(discord.ui.View):
    def __init__(self, label, url):
        super().__init__()
        self.add_item(discord.ui.Button(label=label, url=url))


def setup(bot):
    bot.add_cog(TicketPanel(bot))