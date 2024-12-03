from wrappers.embedWrapper import create_embed
import discord

def create_vouch_embed(author, user, message, stars, attachment_url, vouch_count, embed_settings):
    # Use default values if not set or if explicitly set to None
    title_template = embed_settings.get('title') or "Vouch for {user}"
    description_template = embed_settings.get('description') or ""
    color_value = embed_settings.get('color') or "#3498db"  # Default blue color

    # Replace variables in templates
    try:
        title = title_template.format(user=user.display_name, voucher=author.display_name, message=message, stars=stars, vouch_count=vouch_count)
        description = description_template.format(user=user.display_name, voucher=author.display_name, message=message, stars=stars, vouch_count=vouch_count)
    except KeyError as e:
        raise ValueError(f"Missing placeholder in embed template: {e}")

    # Convert color from hex string to discord.Color
    try:
        color = discord.Color(int(color_value.strip('#'), 16))
    except ValueError:
        raise ValueError(f"Invalid color value: {color_value}")

    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Powered by discord.gg/bailey")
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="Vouch Message", value=message, inline=False)
    embed.add_field(name="Stars", value="⭐" * stars)
    embed.add_field(name="Vouched By", value=author.mention)
    embed.add_field(name="Total Vouches", value=str(vouch_count))
    if attachment_url:
        embed.set_image(url=attachment_url)
    return embed
