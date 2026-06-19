# =====================================================================================================================
# 🤖 VERIFICATION SEQUENCE COG (userVerification.py)
# =====================================================================================================================
# Handles new-member verification: the public verification panel, the
# info-collection modal, and the organizer-facing approve/deny review panel.
# =====================================================================================================================

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput

from cogs.config import (
    GUILD_ID,
    ORGANIZER_ROLE_ID,
    VERIFICATION_CHANNEL_ID,
    VERIFICATION_REVIEW_CHANNEL_ID,
    UNVERIFIED_ROLE_ID,
    VERIFIED_ROLE_ID
)
from cogs.userPermissions import isManager, notAllowed


class DenyReasonModal(Modal, title="Deny Verification"):

    def __init__(self, target_user_id: int):
        super().__init__()
        self.target_user_id = target_user_id

        self.reason = TextInput(
            label="Reason for denial:",
            placeholder="Enter the reason for denying this verification request.",
            required=True,
            max_length=500
        )

        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):

        if not any(role.id == ORGANIZER_ROLE_ID for role in interaction.user.roles):
            return await notAllowed(interaction)

        guild = interaction.guild
        member = guild.get_member(self.target_user_id)

        reason_text = str(self.reason)

        if member:

            try:
                await member.send(
                    f"**❌ Your verification was denied and was kicked from the server!**\nReason: {reason_text}\nYou may try verifying again in a few minutes."
                )
            except:
                pass

            try:
                await member.kick(reason=f"Verification denied! - {reason_text}")
            except:
                pass

        embed = interaction.message.embeds[0]

        embed.color = discord.Color.from_str("#546e7a")
        embed.add_field(
            name="Current Status:",
            value=f"❌ Verification rejected by: {interaction.user.mention}\n**Reason:** {reason_text}",
            inline=False
        )

        await interaction.message.edit(
            embed=embed,
            view=None
        )


class ReviewView(View):

    def __init__(self, target_user_id: int):
        super().__init__(timeout=None)
        self.target_user_id = target_user_id

    @discord.ui.button(
        label="Approve User",
        style=discord.ButtonStyle.success,
        custom_id="verify_approve"
    )
    async def approve(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if not any(role.id == ORGANIZER_ROLE_ID for role in interaction.user.roles):
            return await notAllowed(interaction)

        guild = interaction.guild
        member = guild.get_member(self.target_user_id)

        if not member:
            return await interaction.response.send_message(
                "❌ **An error has occurred!** User has left the server already.",
                ephemeral=True
            )

        verified_role = guild.get_role(VERIFIED_ROLE_ID)
        unverified_role = guild.get_role(UNVERIFIED_ROLE_ID)

        if unverified_role:
            await member.remove_roles(unverified_role)

        if verified_role:
            await member.add_roles(verified_role)

        try:
            await member.send(
                "**✅ Your verification request has been validated!**"
            )
        except:
            pass

        embed = interaction.message.embeds[0]

        embed.color = discord.Color.from_str("#95e147")
        embed.add_field(
            name="Current Status:",
            value=f"✅ Verification approved by: {interaction.user.mention}",
            inline=False
        )

        await interaction.message.edit(
            embed=embed,
            view=None
        )

    @discord.ui.button(
        label="Reject User",
        style=discord.ButtonStyle.danger,
        custom_id="verify_deny"
    )
    async def deny(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if not any(role.id == ORGANIZER_ROLE_ID for role in interaction.user.roles):
            return await notAllowed(interaction)

        await interaction.response.send_modal(
            DenyReasonModal(self.target_user_id)
        )


class VerificationModal(Modal, title="Verification Information"):

    full_name = TextInput(
        label="Enter Full Name:",
        placeholder="e.g. Juan P. Dela Cruz",
        required=True,
        max_length=100
    )

    nickname = TextInput(
        label="Your Nickname:",
        placeholder="e.g. Juan",
        required=True,
        max_length=50
    )

    school = TextInput(
        label="Your School:",
        placeholder="e.g. FEU Institute of Technology",
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):

        review_channel = interaction.guild.get_channel(
            VERIFICATION_REVIEW_CHANNEL_ID
        )

        embed = discord.Embed(
            title="🛂 Create & Conquer 2026 - Verification Request!",
            color=discord.Color.from_str("#fce639")
        )

        embed.add_field(
            name="Discord Username:",
            value=f"{interaction.user.mention} ({interaction.user.name})",
            inline=False
        )

        embed.add_field(
            name="Full Name:",
            value=str(self.full_name),
            inline=False
        )

        embed.add_field(
            name="Nickname:",
            value=str(self.nickname),
            inline=False
        )

        embed.add_field(
            name="School:",
            value=str(self.school),
            inline=False
        )

        await review_channel.send(
            embed=embed,
            view=ReviewView(interaction.user.id)
        )

        await interaction.response.send_message(
            "✅ **Your verification request has been submitted!** Please wait for the organizers to verify...",
            ephemeral=True
        )


class VerificationView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🛂 Verify your account here!",
        style=discord.ButtonStyle.primary,
        custom_id="verification_button"
    )
    async def verify_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        await interaction.response.send_modal(
            VerificationModal()
        )


class UserVerification(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setupverification", description="Creates the verification panel.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def setupverification(self, interaction: discord.Interaction):

        if not isManager(interaction.user):
            return await notAllowed(interaction)

        channel = interaction.guild.get_channel(
            VERIFICATION_CHANNEL_ID
        )

        embed = discord.Embed(
            title="🔒 Verify your account and get access to the Discord Server!",
            description=(
                "**To gain access to the server, complete the verification process!**\n"
                "We will only be asking a **few question** so that we can set your\n"
                "account and have you ready for the **Create & Conquer 2026** event."
            ),
            color=discord.Color.from_str("#4b68e7")
        )

        await channel.send(
            embed=embed,
            view=VerificationView()
        )

        await interaction.response.send_message(
            "✅ The verification panel has been created!",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(UserVerification(bot))
    print("[NEEBOT CNC DEBUGGER] userVerification.seq has been initialized!")