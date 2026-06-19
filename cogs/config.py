# =====================================================================================================================
# ⚙️ CONFIGURATION - LOADS ALL OF NEEBOT'S .ENV VARIABLES & TOKENS!
# =====================================================================================================================
# Single source of truth for every ID/token the cogs need, so userPermissions,
# adminCommands, userVerification, and teamSelector all read from one place
# instead of each calling os.getenv() separately.
# =====================================================================================================================

import os
from dotenv import load_dotenv

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

# Used by teamSelector.py — these were hardcoded numeric IDs in the original
# script. Pulled into .env here so they can be changed without touching code.
# The defaults below match the original hardcoded values exactly.
TEAM_NO_ACCESS_CATEGORY_ID = int(os.getenv("TEAM_NO_ACCESS_CATEGORY_ID", "1516112928775078073"))
FIND_A_TEAM_CHANNEL_ID = int(os.getenv("FIND_A_TEAM_CHANNEL_ID", "1511022035759792263"))

VERSION = "1.1.1"

if not DISCORD_TOKEN:
    raise ValueError(
        "[NEEBOT CNC DEBUGGER] DISCORD_TOKEN was not found in your .env file!"
    )