# =====================================================================================================================
# ❌ PERMISSION HANDLERS (userPermissions.py)
# =====================================================================================================================
# Shared helpers used by every other cog. This file has no slash commands of
# its own, so it is NOT loaded as a discord.py extension (no setup() here) —
# it's just imported directly by adminCommands.py and userVerification.py.
# =====================================================================================================================

import discord

from cogs.config import MANAGER_ROLE_ID


async def notAllowed(interaction: discord.Interaction):
    embed = discord.Embed(
        title="❌・An error has occurred!",
        description="**You are not allowed to do this command.**",
        color=discord.Color.from_str("#aa0000")
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


def isManager(member: discord.Member):
    return any(
        role.id == MANAGER_ROLE_ID
        for role in member.roles
    )