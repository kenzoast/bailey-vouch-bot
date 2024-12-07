import discord
from discord.ext import commands

class StickyMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sticky_messages = {}  # Store sticky message IDs and content for each channel

    @commands.slash_command(name="sticky", description="Set a sticky message in a channel.")
    async def sticky(self, ctx, message: str):
        """Set a sticky message in the current channel."""
        channel_id = ctx.channel.id

        # Check for existing sticky message and delete it
        if channel_id in self.sticky_messages:
            sticky_message_id = self.sticky_messages[channel_id]["message_id"]
            try:
                existing_message = await ctx.channel.fetch_message(sticky_message_id)
                await existing_message.delete()
            except discord.NotFound:
                pass  # If the message no longer exists, continue

        # Send the new sticky message
        sticky_message = await ctx.channel.send(f"📌 **Sticky Message:** {message}")
        self.sticky_messages[channel_id] = {
            "message_id": sticky_message.id,
            "content": message
        }

        await ctx.respond("Sticky message set!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Ensure the sticky message remains at the top of the channel."""
        if message.author.bot:
            return  # Ignore bot messages

        channel_id = message.channel.id
        if channel_id in self.sticky_messages:
            # Fetch the sticky message details
            sticky_message_id = self.sticky_messages[channel_id]["message_id"]
            sticky_content = self.sticky_messages[channel_id]["content"]

            # Delete the sticky message if it exists
            try:
                sticky_message = await message.channel.fetch_message(sticky_message_id)
                await sticky_message.delete()
            except discord.NotFound:
                pass  # Sticky message already deleted

            # Resend the sticky message
            new_sticky_message = await message.channel.send(f"📌 **Sticky Message:** {sticky_content}")
            self.sticky_messages[channel_id]["message_id"] = new_sticky_message.id

def setup(bot):
    bot.add_cog(StickyMessage(bot))
