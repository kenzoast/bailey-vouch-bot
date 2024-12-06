import discord
from discord.ext import commands

class PurgeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='purge', 
        description='Delete a specified number of messages from the channel',
        integration_types={discord.IntegrationType.guild_install}
    )
    async def purge(self, ctx: discord.ApplicationContext, amount: int):
        """Delete a specified number of messages from the channel."""
        # Check if the user has administrator permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("You must have administrator permissions to use this command.", ephemeral=True)
            return

        # Validate the amount
        if amount <= 0:
            await ctx.respond("Please specify a number greater than 0.", ephemeral=True)
            return

        # Limit the maximum number of messages to prevent potential abuse
        if amount > 100:
            await ctx.respond("You can only delete up to 100 messages at a time.", ephemeral=True)
            return

        try:
            # Purge the messages
            deleted = await ctx.channel.purge(limit=amount)
            
            # Respond with the number of deleted messages
            await ctx.respond(f"Successfully deleted {len(deleted)} messages.", ephemeral=True)
        
        except Exception as e:
            await ctx.respond(f"An error occurred while trying to delete messages: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(PurgeCog(bot))
