import discord
from wrappers.embedWrapper import create_embed
import math

# Function to create embeds for the lookup command
def create_lookup_embeds(user, vouches):
    embeds = []
    vouches_per_embed = 5  # Number of vouches per embed
    total_pages = math.ceil(len(vouches) / vouches_per_embed)

    for page in range(total_pages):
        embed = create_embed(
            title=f"Vouches for {user.display_name} (Page {page + 1}/{total_pages})",
            color=discord.Color.blue()
        )
        start = page * vouches_per_embed
        end = start + vouches_per_embed
        for vouch in vouches[start:end]:
            voucher = f"<@{vouch['voucher_id']}>"
            stars = "⭐" * vouch['stars']
            message = vouch['message']
            embed.add_field(
                name=f"{stars} by {voucher}",
                value=message,
                inline=False
            )
        embeds.append(embed)
    return embeds
