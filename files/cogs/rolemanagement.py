import discord
from discord.ext import commands

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="addrole", description="Add a role to a user.")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx: discord.ApplicationContext, member: discord.Member, role: discord.Role):
        """
        Add a role to a user.
        - member: The member to give the role to.
        - role: The role to assign to the member.
        """
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.respond("I do not have permission to manage roles.", ephemeral=True)
            return

        if role >= ctx.guild.me.top_role:
            await ctx.respond("I cannot assign a role higher or equal to my top role.", ephemeral=True)
            return

        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.respond("You cannot assign a role higher or equal to your top role.", ephemeral=True)
            return

        if role in member.roles:
            await ctx.respond(f"{member.mention} already has the {role.name} role.", ephemeral=True)
            return

        try:
            await member.add_roles(role, reason=f"Role added by {ctx.author}")
            await ctx.respond(f"Successfully added the {role.name} role to {member.mention}.")
        except discord.Forbidden:
            await ctx.respond("I do not have permission to assign this role.", ephemeral=True)
        except discord.HTTPException as e:
            await ctx.respond(f"An error occurred while adding the role: {e}", ephemeral=True)

    @commands.slash_command(name="removerole", description="Remove a role from a user.")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx: discord.ApplicationContext, member: discord.Member, role: discord.Role):
        """
        Remove a role from a user.
        - member: The member to remove the role from.
        - role: The role to remove.
        """
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.respond("I do not have permission to manage roles.", ephemeral=True)
            return

        if role >= ctx.guild.me.top_role:
            await ctx.respond("I cannot remove a role higher or equal to my top role.", ephemeral=True)
            return

        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.respond("You cannot remove a role higher or equal to your top role.", ephemeral=True)
            return

        if role not in member.roles:
            await ctx.respond(f"{member.mention} does not have the {role.name} role.", ephemeral=True)
            return

        try:
            await member.remove_roles(role, reason=f"Role removed by {ctx.author}")
            await ctx.respond(f"Successfully removed the {role.name} role from {member.mention}.")
        except discord.Forbidden:
            await ctx.respond("I do not have permission to remove this role.", ephemeral=True)
        except discord.HTTPException as e:
            await ctx.respond(f"An error occurred while removing the role: {e}", ephemeral=True)

def setup(bot):
    bot.add_cog(RoleManagement(bot))
