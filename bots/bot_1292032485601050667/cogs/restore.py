import discord
from discord.ext import commands
from utils import database  # Assuming 'db' is the correct module name
from wrappers.embedWrapper import create_embed
from embeds.vouch_embed import create_vouch_embed
from datetime import timedelta
import constants


OWNER_ID = constants.OWNER_ID

class RestoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="restore", description="Send all vouches in this channel (Owner only)")
    async def restore(self, ctx):
        # Check if the user is the bot owner
        if ctx.author.id != OWNER_ID:
            error_embed = create_embed(
                title="Permission Denied",
                description="You must be the bot owner to use this command.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        await ctx.defer(ephemeral=False)

        # Get all vouches for the guild
        vouches = database.get_all_vouches()
        if not vouches:
            embed = create_embed(
                title="No Vouches Found",
                description="There are no vouches to restore.",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed)
            return

        # Get embed settings
        embed_settings = database.get_embed_settings(ctx.guild.id) or {}

        # Send each vouch as an individual message
        for vouch in vouches:
            user = ctx.guild.get_member(vouch['user_id'])
            voucher = ctx.guild.get_member(vouch['voucher_id'])
            if not user or not voucher:
                continue  # Skip if user or voucher is not found

            # Get the vouch count for the user
            vouch_count = database.get_vouch_count(user.id)

            # Create the vouch embed
            embed = create_vouch_embed(
                author=voucher,
                user=user,
                message=vouch['message'],
                stars=vouch['stars'],
                attachment_url=vouch.get('attachment_url'),
                vouch_count=vouch_count,
                embed_settings=embed_settings
            )

            # Send the embed to the channel
            await ctx.channel.send(embed=embed)

            # Optional: Add a short delay to avoid hitting rate limits
            await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(milliseconds=250))

        # Send a confirmation message
        success_embed = create_embed(
            title="Vouches Restored",
            description="All vouches have been restored in this channel.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=success_embed)

def setup(bot):
    bot.add_cog(RestoreCog(bot))
