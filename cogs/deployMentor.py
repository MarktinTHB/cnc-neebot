# =====================================================================================================================
# 🎓 DEPLOY MENTOR SEQUENCE COG (deployMentor.py)
# =====================================================================================================================
# Automatically deploys mentor role and selected users to all team channels.
#
# Features:
# - /deploymentors
#       Deploy mentor role to all current channels
#       Future channels are automatically handled
#
# - /deployuser @user
#       Deploy user to all current channels
#       Future channels are automatically handled
#
# - Persists deployed users through bot restarts
# =====================================================================================================================

import json
import os

import discord
from discord import app_commands
from discord.ext import commands

from cogs.config import (
    GUILD_ID,
    MANAGER_ROLE_ID,
    MENTOR_ROLE_ID,
    TEAM_CATEGORY_ID
)

DEPLOY_FILE = "deployed_users.json"


class DeployMentor(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.deployed_users = self.load_deployed_users()

    # =====================================================
    # JSON STORAGE
    # =====================================================

    def load_deployed_users(self):
        if not os.path.exists(DEPLOY_FILE):
            return set()

        try:
            with open(DEPLOY_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()

    def save_deployed_users(self):
        with open(DEPLOY_FILE, "w") as f:
            json.dump(list(self.deployed_users), f)

    # =====================================================
    # HELPER
    # =====================================================

    def is_manager(self, member: discord.Member):
        return any(role.id == MANAGER_ROLE_ID for role in member.roles)

    async def apply_permissions(self, channel, target):

        overwrite = channel.overwrites_for(target)

        if isinstance(channel, discord.TextChannel):
            overwrite.view_channel = True
            overwrite.send_messages = True
            overwrite.read_message_history = True

        elif isinstance(channel, discord.VoiceChannel):
            overwrite.view_channel = True
            overwrite.connect = True
            overwrite.speak = True

        elif isinstance(channel, discord.StageChannel):
            overwrite.view_channel = True
            overwrite.connect = True

        await channel.set_permissions(
            target,
            overwrite=overwrite
        )

    # =====================================================
    # DEPLOY MENTORS
    # =====================================================

    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(
        name="deploymentors",
        description="Deploy mentor permissions to all team channels."
    )
    async def deploymentors(self, interaction: discord.Interaction):

        if not self.is_manager(interaction.user):
            await interaction.response.send_message(
                "❌ Only Managers can use this command.",
                ephemeral=True
            )
            return

        guild = interaction.guild

        mentor_role = guild.get_role(MENTOR_ROLE_ID)
        category = guild.get_channel(TEAM_CATEGORY_ID)

        if mentor_role is None:
            await interaction.response.send_message(
                "❌ Mentor role not found.",
                ephemeral=True
            )
            return

        if category is None:
            await interaction.response.send_message(
                "❌ Team category not found.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        updated = 0

        for channel in category.channels:
            await self.apply_permissions(channel, mentor_role)
            updated += 1

        await interaction.followup.send(
            f"✅ Mentor role deployed to **{updated}** channels.\n"
            f"Future channels will automatically receive mentor permissions.",
            ephemeral=True
        )

    # =====================================================
    # DEPLOY USER
    # =====================================================

    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(
        name="deployuser",
        description="Grant a user access to all team channels."
    )
    @app_commands.describe(
        user="User to deploy to all team channels"
    )
    async def deployuser(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        if not self.is_manager(interaction.user):
            await interaction.response.send_message(
                "❌ Only Managers can use this command.",
                ephemeral=True
            )
            return

        category = interaction.guild.get_channel(TEAM_CATEGORY_ID)

        if category is None:
            await interaction.response.send_message(
                "❌ Team category not found.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        updated = 0

        for channel in category.channels:
            await self.apply_permissions(channel, user)
            updated += 1

        self.deployed_users.add(user.id)
        self.save_deployed_users()

        await interaction.followup.send(
            f"✅ {user.mention} has been deployed to **{updated}** channels.\n"
            f"Future channels will automatically include them.",
            ephemeral=True
        )

    # =====================================================
    # OPTIONAL UNDEPLOY USER
    # =====================================================

    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.command(
        name="undeployuser",
        description="Remove a deployed user."
    )
    async def undeployuser(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        if not self.is_manager(interaction.user):
            await interaction.response.send_message(
                "❌ Only Managers can use this command.",
                ephemeral=True
            )
            return

        if user.id in self.deployed_users:
            self.deployed_users.remove(user.id)
            self.save_deployed_users()

        await interaction.response.send_message(
            f"✅ {user.mention} removed from automatic deployments.",
            ephemeral=True
        )

    # =====================================================
    # AUTO DEPLOY TO NEW CHANNELS
    # =====================================================

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        try:

            if channel.category_id != TEAM_CATEGORY_ID:
                return

            guild = channel.guild

            mentor_role = guild.get_role(MENTOR_ROLE_ID)

            if mentor_role:
                await self.apply_permissions(
                    channel,
                    mentor_role
                )

            for user_id in self.deployed_users:

                member = guild.get_member(user_id)

                if member is None:
                    continue

                await self.apply_permissions(
                    channel,
                    member
                )

            print(
                f"[DEPLOYMENT] Auto-deployed permissions to new channel: {channel.name}"
            )

        except Exception as e:
            print(
                f"[DEPLOYMENT ERROR] {e}"
            )


async def setup(bot):
    await bot.add_cog(DeployMentor(bot))


print("[NEEBOT CNC DEBUGGER] deployMentor.seq has been initialized!")