# =====================================================================================================================
# 🤖 CPEO'S DISCORD NEEBOT - CREATE AND CONQUER 2026
# Project created for: Computer Engineering Organization - FEU Institute of Technology
# Developers: Sean Martin Tabelisma (@marktinthb) & Pauleen Ann Rivera (@pannchum)
# =====================================================================================================================
# Entry point. Loads every cog and starts the bot. Run this file (not the
# files inside cogs/) to start NeeBot: `python main.py`
# =====================================================================================================================

import logging

import discord
from discord.ext import commands

from cogs.config import DISCORD_TOKEN, GUILD_ID, VERSION

handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)

intents = discord.Intents.default()
intents.members = True


class NeeBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="-", intents=intents)

    async def setup_hook(self):

        # userPermissions.py has no slash commands of its own (just shared
        # helpers imported by the other cogs), so it isn't loaded as an
        # extension here — only cogs that register commands need load_extension.
        for extension in ("cogs.adminCommands", "cogs.userVerification", "cogs.teamSelector"):
            await self.load_extension(extension)

        print("[NEEBOT CNC DEBUGGER] botCommands.seq has been initialized!")

        # Re-register the verification panel as a persistent view so its
        # button keeps working after a bot restart. This is safe because
        # VerificationView takes no dynamic arguments and its button has an
        # explicit custom_id. ReviewView/JoinTeamButtonView/TeamSelectorView
        # carry per-instance data (target user, team name) or lack custom_ids,
        # so — same as in the original single-file script — they only stay
        # interactive for as long as the bot process stays alive.
        from cogs.userVerification import VerificationView
        self.add_view(VerificationView())

        try:
            synced = await self.tree.sync(guild=discord.Object(id=GUILD_ID))
            print(f"[NEEBOT CNC DEBUGGER] Synced and loaded {len(synced)} slash commands!")
        except Exception as e:
            print(f"[NEEBOT CNC DEBUGGER] An error has occurred! Sync failed: {e}.")


bot = NeeBot()

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now online!")
    print(f"✅ Guild ID Loaded: {GUILD_ID}")

    botActivity = discord.Activity(
        type=discord.ActivityType.playing,
        name=f"🧠 Join the battle! | [v{VERSION}]",
        state="createconquerhackathon.vercel.app"
    )

    await bot.change_presence(
        activity=botActivity,
        status=discord.Status.online
    )

    print("[NEEBOT CNC DEBUGGER] botActivity.seq has been initialized!")


# =====================================================================================================================
# 🔒 DO NOT TOUCH! KEEPS THE DISCORD BOT RUNNING.
# =====================================================================================================================

if __name__ == "__main__":
    bot.run(
        DISCORD_TOKEN,
        log_handler=handler,
        log_level=logging.DEBUG
    )
