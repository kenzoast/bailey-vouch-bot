import discord
from discord.ext import commands
from discord import Option
from utils import database
from wrappers.embedWrapper import create_embed
from embeds.vouch_embed import create_vouch_embed

class VouchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command for /vouch
    @commands.slash_command(name="vouch", description="Leave a vouch for a user")
    async def vouch(
        self,
        ctx,
        user: Option(discord.User, "Select a user to vouch for"),
        message: Option(str, "Your vouch message"),
        stars: Option(int, "Rating out of 5 stars", choices=[1, 2, 3, 4, 5]),
        attachment: Option(discord.Attachment, "Optional attachment", required=False)
    ):
        await ctx.defer(ephemeral=True)

        # Get the required role from the config
        required_role_id = database.get_vouch_role(ctx.guild.id)
        if required_role_id:
            required_role = ctx.guild.get_role(required_role_id)
            if required_role not in ctx.author.roles:
                error_embed = create_embed(
                    title="Permission Denied",
                    description=f"You must have the {required_role.name} role to use this command.",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=error_embed, ephemeral=True)
                return

        attachment_url = attachment.url if attachment else None

        # Save the vouch to the database
        database.save_vouch(user.id, ctx.author.id, message, stars, attachment_url)

        # Get the vouch count for the user
        vouch_count = database.get_vouch_count(user.id)

        # Get the embed settings
        embed_settings = database.get_embed_settings(ctx.guild.id) or {}

        # Get the vouch channel from the config
        vouch_channel_id = database.get_vouch_channel(ctx.guild.id)
        if vouch_channel_id:
            vouch_channel = self.bot.get_channel(vouch_channel_id)
            if vouch_channel:
                # Create and send the vouch embed
                embed = create_vouch_embed(ctx.author, user, message, stars, attachment_url, vouch_count, embed_settings)
                await vouch_channel.send(embed=embed)
            else:
                error_embed = create_embed(
                    title="Vouch Channel Not Found",
                    description="Vouch channel not found. Please reconfigure.",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=error_embed, ephemeral=True)
                return
        else:
            error_embed = create_embed(
                title="Vouch Channel Not Set",
                description="Vouch channel is not set. Please use /configure to set it.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        success_embed = create_embed(
            title="Vouch Recorded",
            description="Your vouch has been recorded and sent to the vouch channel.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=success_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(VouchCog(bot))
