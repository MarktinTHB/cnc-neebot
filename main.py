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

# =====================================================================================================================
# ⚙️ LOAD DISCORD BOT'S .ENV VARIABLES & TOKENS!
# =====================================================================================================================

load_dotenv()

GUILD_ID = int(os.getenv("GUILD_ID"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_DEVELOPERS = os.getenv("BOT_DEVELOPERS")
MANAGER_ROLE_ID = int(os.getenv("MANAGER_ROLE_ID"))
ORGANIZER_ROLE_ID = int(os.getenv("ORGANIZER_ROLE_ID"))

versionValue = "1.0.3"

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

# TBD: Will be done by @pannchum
# Function: Needs to have a text display on #verification with a button.
# (Like what we have currently on the server @Appy).

# Button will prompt a menu that will ask the following questions:
# Full Name: (e.g. Juan P. Dela Cruz)
# Nickname: (e.g. Juan)
# School: (e.g. FEU Institute of Technology)

# Once they fill all of this out, it will send it on a specific channel for organizer's to verify.
# Approve or Deny button will show in that channel, if approved by organizers, they will be removed from the Unverified Role.
# They will be added on Verified role to access the channels.

# If denied, organizer's will be prompted a menu asking a reason for declining, user will be kicked from the server and will
# be sent a message of why they were denied for verification.


# =====================================================================================================================
# 🤖 TEAM SELECTOR SEQUENCE: CREATES/JOIN A SPECIFIC TEAM IN CHANNEL (teamSelector.seq)
# =====================================================================================================================

# TBD: Will be done by @marktinthb



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