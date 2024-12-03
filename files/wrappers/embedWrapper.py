import discord

FOOTER_TEXT = "Baily Vouch Bot"  # Permanent footer text
FOOTER_ICON_URL = "https://media.discordapp.net/attachments/1312813869349208122/1312855053555466350/Untitled_design_12.png?ex=674e030c&is=674cb18c&hm=f935f334fcc018b7b9550d1bceb8fd2135f7e573fddf40bdaaec75ba665e3aad&="  # Optional footer icon URL

# Wrapper function to create embeds with a permanent footer
def create_embed(title=None, description=None, color=discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON_URL)
    return embed
