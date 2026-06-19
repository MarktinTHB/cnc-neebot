# =====================================================================================================================
# 🤖 CPEO'S DISCORD NEEBOT - CREATE AND CONQUER 2026
# Project created for: Computer Engineering Organization - FEU Institute of Technology
# Developers: Sean Martin Tabelisma (@marktinthb) & Pauleen Ann Rivera (@pannchum)
# =====================================================================================================================

import os
import discord
import logging

from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput

# =====================================================================================================================
# ⚙️ LOAD DISCORD BOT'S .ENV VARIABLES & TOKENS!
# =====================================================================================================================

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_DEVELOPERS = os.getenv("BOT_DEVELOPERS")

GUILD_ID = int(os.getenv("GUILD_ID"))
MANAGER_ROLE_ID = int(os.getenv("MANAGER_ROLE_ID"))
ORGANIZER_ROLE_ID = int(os.getenv("ORGANIZER_ROLE_ID"))
VERIFICATION_CHANNEL_ID = int(os.getenv("VERIFICATION_CHANNEL_ID"))
VERIFICATION_REVIEW_CHANNEL_ID = int(os.getenv("VERIFICATION_REVIEW_CHANNEL_ID"))
UNVERIFIED_ROLE_ID = int(os.getenv("UNVERIFIED_ROLE_ID"))
VERIFIED_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID"))

versionValue = "1.1.1"

# =====================================================================================================================
# 💾 DISCORD INITIATION SETUP!
# =====================================================================================================================

handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="-",
    intents=intents
)

# =====================================================================================================================
# ❌ PERMISSION HANDLERS: DEFAULT MESSAGE FOR NO PERMISSIONS.
# =====================================================================================================================

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

# =====================================================================================================================
# 🤖 ACTIVATION: LOADS ALL DISCORD BOT'S COMMANDS AND SEQUENCES.
# =====================================================================================================================

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now online!")
    print(f"✅ Guild ID Loaded: {GUILD_ID}")

    try:
        synced = await bot.tree.sync(
            guild=discord.Object(id=GUILD_ID)
        )
        print("[NEEBOT CNC DEBUGGER] botCommands.seq has been initialized!")
        print(f"[NEEBOT CNC DEBUGGER] Synced and loaded {len(synced)} slash commands!")
    except Exception as e:
        print(f"[NEEBOT CNC DEBUGGER] An error has occurred! Sync failed: {e}.")

    botActivity = discord.Activity(
        type=discord.ActivityType.playing,
        name=f"🧠 Join the battle! | [v{versionValue}]",
        state="createconquerhackathon.vercel.app"
    )

    await bot.change_presence(
        activity=botActivity,
        status=discord.Status.online
    )

    print("[NEEBOT CNC DEBUGGER] botActivity.seq has been initialized!")

# =====================================================================================================================
# 🤖 VERIFICATION SEQUENCE: VERIFY USERS AND GRANTS ACCESS TO THE SERVER (userVerification.seq)
# =====================================================================================================================

    print("[NEEBOT CNC DEBUGGER] userVerification.seq has been initialized!")

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


@bot.tree.command(
    name="setupverification",
    description="Creates the verification panel.",
    guild=discord.Object(id=GUILD_ID)
)
async def setupverification(interaction: discord.Interaction):

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


teams = {}


class CreateTeamModal(Modal, title="Create a Team"):

    team_name = TextInput(
        label="Team Name",
        placeholder="Enter your team name",
        required=True,
        max_length=50
    )

    description = TextInput(
        label="Description / Requirements",
        placeholder="What is your team about?",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=300
    )

    team_size = TextInput(
        label="Team Size (4-6 only)",
        placeholder="Enter number between 4-6",
        required=True,
        max_length=1
    )

    password = TextInput(
        label="Team Password (optional)",
        placeholder="Leave blank for public team",
        required=False,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):

        print(f"[TEAM DEBUG] Creating team: {self.team_name.value}")

        guild = interaction.guild
        creator = interaction.user

        name = self.team_name.value.strip()

        if name in teams:
            return await interaction.response.send_message(
                "❌ A team with this name already exists.",
                ephemeral=True
            )

        try:
            size = int(self.team_size.value)
            if size < 4 or size > 6:
                raise ValueError()
        except:
            return await interaction.response.send_message(
                "❌ Team size must be 4-6 only.",
                ephemeral=True
            )

        is_private = bool(self.password.value.strip())

        print(f"[TEAM DEBUG] Size={size}, Private={is_private}, Creator={creator}")

        team_role = await guild.create_role(name=f"TEAM - {name}")
        await creator.add_roles(team_role)

        print(f"[TEAM DEBUG] Role created: {team_role.id}")

        no_access_category = guild.get_channel(1516112928775078073)

        # =========================================================
        # CHANNEL CREATION (FIXED PERMISSIONS)
        # =========================================================

        text_channel = await guild.create_text_channel(
            name=f"team-{name.lower().replace(' ', '-')}",
            category=no_access_category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
        )

        voice_channel = await guild.create_voice_channel(
            name=f"🔊 {name}",
            category=no_access_category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
        )

        print(f"[TEAM DEBUG] Channels created: {text_channel.id}, {voice_channel.id}")

        # GIVE ROLE ACCESS TO CHANNELS
        await text_channel.set_permissions(
            team_role,
            view_channel=True,
            send_messages=True
        )

        await voice_channel.set_permissions(
            team_role,
            view_channel=True,
            connect=True,
            speak=True
        )

        print(f"[TEAM DEBUG] Permissions applied for role {team_role.id}")

        teams[name] = {
            "name": name,
            "description": self.description.value,
            "size": size,
            "password": self.password.value if is_private else None,
            "creator": creator.id,
            "role_id": team_role.id,
            "text_id": text_channel.id,
            "voice_id": voice_channel.id,
            "members": [creator.id],
            "private": is_private
        }

        print(f"[TEAM DEBUG] Team stored: {name}")

        find_channel = guild.get_channel(1511022035759792263)

        embed = discord.Embed(
            title=f"🫂 {name}",
            description=self.description.value,
            color=discord.Color.blue() if is_private else discord.Color.green()
        )

        embed.add_field(name="Team Size", value=str(size), inline=True)
        embed.add_field(name="Slots Left", value=str(size - 1), inline=True)
        embed.add_field(name="Type", value="Private 🔵" if is_private else "Public 🟢", inline=True)

        view = JoinTeamButtonView(name)

        await find_channel.send(embed=embed, view=view)

        print(f"[TEAM DEBUG] Posted team '{name}' in find-a-team channel")

        await interaction.response.send_message(
            f"✅ Team **{name}** created successfully!",
            ephemeral=True
        )


class JoinTeamButtonView(View):

    def __init__(self, team_name: str):
        super().__init__(timeout=None)
        self.team_name = team_name

    @discord.ui.button(label="Join Team", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: Button):

        team = teams.get(self.team_name)

        if not team:
            return await interaction.response.send_message(
                "❌ Team no longer exists.",
                ephemeral=True
            )

        print(f"[TEAM DEBUG] {interaction.user} attempting to join {team['name']}")

        if len(team["members"]) >= team["size"]:
            return await interaction.response.send_message(
                "❌ Team is full.",
                ephemeral=True
            )

        if team["private"]:
            await interaction.response.send_modal(JoinTeamPasswordModal(self.team_name))
            return

        await self.add_member(interaction, team)

    async def add_member(self, interaction: discord.Interaction, team: dict):

        guild = interaction.guild
        member = interaction.user

        role = guild.get_role(team["role_id"])

        await member.add_roles(role)

        team["members"].append(member.id)

        print(f"[TEAM DEBUG] {member} joined {team['name']}")

        remaining = team["size"] - len(team["members"])

        embed = interaction.message.embeds[0]
        embed.set_field_at(1, name="Slots Left", value=str(remaining), inline=True)

        await interaction.message.edit(embed=embed)

        await interaction.response.send_message(
            f"✅ You joined **{team['name']}**!",
            ephemeral=True
        )


class JoinTeamPasswordModal(Modal, title="Enter Team Password"):

    def __init__(self, team_name: str):
        super().__init__()
        self.team_name = team_name

    password = TextInput(label="Password", required=True)

    async def on_submit(self, interaction: discord.Interaction):

        team = teams.get(self.team_name)

        print(f"[TEAM DEBUG] Password attempt for {self.team_name}")

        if not team:
            return await interaction.response.send_message(
                "❌ Team no longer exists.",
                ephemeral=True
            )

        if self.password.value != team["password"]:
            print("[TEAM DEBUG] Wrong password")
            return await interaction.response.send_message(
                "❌ Incorrect password.",
                ephemeral=True
            )

        print("[TEAM DEBUG] Password correct")

        view = JoinTeamButtonView(self.team_name)
        await view.add_member(interaction, team)


class TeamSelectorView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Team", style=discord.ButtonStyle.primary)
    async def create(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CreateTeamModal())

    @discord.ui.button(label="Join Team", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: Button):

        if not teams:
            return await interaction.response.send_message(
                "❌ No teams available yet.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🫂 Available Teams",
            description="\n".join([f"**{t}**" for t in teams.keys()]),
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="team",
    description="Create or join a team",
    guild=discord.Object(id=GUILD_ID)
)
async def team(interaction: discord.Interaction):

    print(f"[TEAM DEBUG] /team used by {interaction.user}")

    await interaction.response.send_message(
        "🫂 Team Selector Menu",
        view=TeamSelectorView(),
        ephemeral=True
    )


print("[NEEBOT CNC DEBUGGER] teamSelector.seq has been initialized!")
# =====================================================================================================================
# 🎩 ADMIN COMMAND: OP COMMAND (/op)
# =====================================================================================================================

@bot.tree.command(
    name="op",
    description="Gives organizer role to a user.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(user="User will receive organizer's privileges.")
async def op(interaction: discord.Interaction, user: discord.Member):

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

# =====================================================================================================================
# 🎩 ADMIN COMMAND: DEOP COMMAND (/deop)
# =====================================================================================================================

@bot.tree.command(
    name="deop",
    description="Removes organizer role from a user.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(user="User will lose organizer's privileges.")
async def deop(interaction: discord.Interaction, user: discord.Member):

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

# =====================================================================================================================
# 🎩 ADMIN COMMAND: PING COMMAND (/ping)
# =====================================================================================================================

@bot.tree.command(
    name="ping",
    description="Displays the ping latency of the bot.",
    guild=discord.Object(id=GUILD_ID)
)
async def ping(interaction: discord.Interaction):

    if not interaction.guild:
        return await interaction.response.send_message(
            "❌ This command can't be used in DMs.",
            ephemeral=True
        )

    if not isManager(interaction.user):
        return await notAllowed(interaction)

    latencyValue = round(bot.latency * 1000)

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

# =====================================================================================================================
# 🔒 DO NOT TOUCH! KEEPS THE DISCORD BOT RUNNING.
# =====================================================================================================================

if not DISCORD_TOKEN:
    raise ValueError(
        "[NEEBOT CNC DEBUGGER] DISCORD_TOKEN was not found in your .env file!"
    )

bot.run(
    DISCORD_TOKEN,
    log_handler=handler,
    log_level=logging.DEBUG
)