# =====================================================================================================================
# 🎩 ADMIN COMMANDS COG (adminCommands.py)
# =====================================================================================================================
# /op, /deop, /ping
# =====================================================================================================================

import discord
from discord.ext import commands
from discord import app_commands

from cogs.config import GUILD_ID, ORGANIZER_ROLE_ID
from cogs.userPermissions import isManager, notAllowed


class AdminCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ===================================================================================================
    # 🎩 ADMIN COMMAND: OP COMMAND (/op)
    # ===================================================================================================

    @app_commands.command(name="op", description="Gives organizer role to a user.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(user="User will receive organizer's privileges.")
    async def op(self, interaction: discord.Interaction, user: discord.Member):

        if not isManager(interaction.user):
            return await notAllowed(interaction)

        role = interaction.guild.get_role(ORGANIZER_ROLE_ID)

        if role is None:
            return await interaction.response.send_message(
                "❌ No role is detected in this server!",
                ephemeral=True
            )

        if isManager(user):
            return await interaction.response.send_message(
                "❌ This user is already opped!",
                ephemeral=True
            )

        await user.add_roles(role)

        embed = discord.Embed(
            title="🎩 You have assigned an organizer!",
            description=f"{user.mention} has been given {role.mention}.",
            color=discord.Color.from_str("#4b68e7")
        )

        await interaction.response.send_message(embed=embed)

    # ===================================================================================================
    # 🎩 ADMIN COMMAND: DEOP COMMAND (/deop)
    # ===================================================================================================

    @app_commands.command(name="deop", description="Removes organizer role from a user.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(user="User will lose organizer's privileges.")
    async def deop(self, interaction: discord.Interaction, user: discord.Member):

        if not isManager(interaction.user):
            return await notAllowed(interaction)

        role = interaction.guild.get_role(ORGANIZER_ROLE_ID)

        if role is None:
            return await interaction.response.send_message(
                "❌ No role is detected in this server!",
                ephemeral=True
            )

        if isManager(user):
            return await interaction.response.send_message(
                "❌ You cannot deop a manager!",
                ephemeral=True
            )

        await user.remove_roles(role)

        embed = discord.Embed(
            title="🎩 You have removed an organizer!",
            description=f"{user.mention} has been removed from {role.mention}.",
            color=discord.Color.from_str("#4b68e7")
        )

        await interaction.response.send_message(embed=embed)

    # ===================================================================================================
    # 🎩 ADMIN COMMAND: PING COMMAND (/ping)
    # ===================================================================================================

    @app_commands.command(name="ping", description="Displays the ping latency of the bot.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def ping(self, interaction: discord.Interaction):

        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ This command can't be used in DMs.",
                ephemeral=True
            )

        if not isManager(interaction.user):
            return await notAllowed(interaction)

        latencyValue = round(self.bot.latency * 1000)

        if latencyValue < 100:
            color = discord.Color.from_str("#a8d0fc")
            status = "Stable"
        elif latencyValue < 200:
            color = discord.Color.from_str("#fce56b")
            status = "Unstable"
        else:
            color = discord.Color.from_str("#fab4bc")
            status = "Critical"

        embed = discord.Embed(
            title="Checking the bot's status...",
            description=(
                f"**Latency:** `{latencyValue} ms`\n"
                f"**Current Status:** `{status}`"
            ),
            color=color
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
    print("[NEEBOT CNC DEBUGGER] adminCommands.seq has been initialized!")