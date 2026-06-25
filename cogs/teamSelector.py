# =====================================================================================================================
# 🫂 TEAM SELECTOR SEQUENCE COG (teamSelector.py)
# =====================================================================================================================
# Handles team creation, the public "find a team" panel, and joining a team
# (public or password-protected).
# =====================================================================================================================

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput

from cogs.config import GUILD_ID, TEAM_NO_ACCESS_CATEGORY_ID, FIND_A_TEAM_CHANNEL_ID

# In-memory team registry, shared by every view/modal in this cog.
teams = {}


class CreateTeamModal(Modal, title="Assemble Team"):

    team_name = TextInput(
        label="Team Name:",
        placeholder="Every team starts with a legendary name!",
        required=True,
        max_length=50
    )

    description = TextInput(
        label="Description & Requirements:",
        placeholder="Tell us what's your team all about and what kind of teammate are you looking for?",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=300
    )

    team_size = TextInput(
        label="Team Size:",
        placeholder="You may only recruit 4 to 6 members!",
        required=True,
        max_length=1
    )

    password = TextInput(
        label="Team Code:",
        placeholder="By leaving this blank, anyone can join your team!",
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
                "❌ Uh oh! A team with this name already exists.",
                ephemeral=True
            )

        try:
            size = int(self.team_size.value)
            if size < 4 or size > 6:
                raise ValueError()
        except:
            return await interaction.response.send_message(
                "❌ Your team must consist of 4 to 6 members only!",
                ephemeral=True
            )

        is_private = bool(self.password.value.strip())

        print(f"[TEAM DEBUG] Size={size}, Private={is_private}, Creator={creator}")

        team_role = await guild.create_role(name=f"👥｜{name}")
        await creator.add_roles(team_role)

        print(f"[TEAM DEBUG] Role created: {team_role.id}")

        no_access_category = guild.get_channel(TEAM_NO_ACCESS_CATEGORY_ID)

        # =========================================================
        # CHANNEL CREATION (FIXED PERMISSIONS)
        # =========================================================

        text_channel = await guild.create_text_channel(
            name=f"🤝｜team-{name.lower().replace(' ', '-')}",
            category=no_access_category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
        )

        voice_channel = await guild.create_voice_channel(
            name=f"🔊・{name} Lounge",
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

        await text_channel.send(
            f"👋 Welcome to your team channel, {creator.mention}!\n\n"
            f"🌟 **Team Name:** {name}\n"
            f"👥 **Team Size:** {size}\n"
            f"🔒 **Team Type:** {'Private' if is_private else 'Public'}\n\n"
            f"Use this channel to coordinate with your teammates, share ideas, and prepare for Create & Conquer 2026!"
        )

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

        find_channel = guild.get_channel(FIND_A_TEAM_CHANNEL_ID)

        embed = discord.Embed(
            title=f"🔎・Team {name} are looking for a teammate!",
            description=f"> **Description & Requirements:** {self.description.value}",
            color=discord.Color.from_str("#fce639")
        )

        embed.add_field(
            name="👑 Team Leader:",
            value=creator.mention,
            inline=True
        )

        embed.add_field(
            name="👥 Team Size:",
            value=f"**`{len(teams[name]['members'])}`/`{size}`**",
            inline=True
        )

        embed.add_field(
            name="🔒 Team Type:" if is_private else "🔓 Team Type:",
            value="**Private**" if is_private else "**Public**",
            inline=True
        )

        embed.set_footer(
            text="🧐・Interested in joining? You can click the button below to join this team!"
        )

        view = JoinTeamButtonView(name)

        await find_channel.send(embed=embed, view=view)

        print(f"[TEAM DEBUG] Posted team '{name}' in find-a-team channel")

        await interaction.response.send_message(
            f"✅ Your team **{name}** has been created successfully!",
            ephemeral=True
        )


class JoinTeamButtonView(View):

    def __init__(self, team_name: str):
        super().__init__(timeout=None)
        self.team_name = team_name

    @discord.ui.button(label="🔎 Join this Team!", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: Button):

        team = teams.get(self.team_name)

        if not team:
            return await interaction.response.send_message(
                "❌ This team has dissolved and no longer exists!",
                ephemeral=True
            )

        print(f"[TEAM DEBUG] {interaction.user} attempting to join {team['name']}")

        if len(team["members"]) >= team["size"]:
            return await interaction.response.send_message(
                "❌ Sorry! This team is already full.",
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
            f"✅ You have joined the **{team['name']}**!",
            ephemeral=True
        )


class JoinTeamPasswordModal(Modal, title="Team Code Required!"):

    def __init__(self, team_name: str):
        super().__init__()
        self.team_name = team_name

    password = TextInput(label="Team Code:", required=True)

    async def on_submit(self, interaction: discord.Interaction):

        team = teams.get(self.team_name)

        print(f"[TEAM DEBUG] Password attempt for {self.team_name}")

        if not team:
            return await interaction.response.send_message(
                "❌ This team has dissolved and no longer exists!",
                ephemeral=True
            )

        if self.password.value != team["password"]:
            print("[TEAM DEBUG] Wrong password")
            return await interaction.response.send_message(
                "❌ Incorrect password! Try again later, and ask the leader for the code.",
                ephemeral=True
            )

        print("[TEAM DEBUG] Password correct")

        view = JoinTeamButtonView(self.team_name)
        await view.add_member(interaction, team)


class TeamSelectorView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🌟 Assemble a Team!", style=discord.ButtonStyle.success)
    async def create(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CreateTeamModal())

class TeamSelector(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="teamdeploy",
        description="Deploy the Team Selector panel."
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def deploy_team_selector(self, interaction: discord.Interaction):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ You do not have permission to use this command!",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🫂・Create and Conquer 2026 - Team Selector",
            description=(
                "**Looking for teammates or ready to build your dream team?**\n"
                "🌟 **Assemble a team!** — Create your own team and recruit members.\n"
                "🔎 **Join a team!** — Browse available teams here and join one that matches your interests.\n"
            ),
            color=discord.Color.gold()
        )

        await interaction.channel.send(
            embed=embed,
            view=TeamSelectorView()
        )

        await interaction.response.send_message(
            "✅ Team Selector panel deployed!",
            ephemeral=True
        )

    @app_commands.command(
        name="syncteam",
        description="Force create a team and automatically assign members."
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def sync_team(
            self,
            interaction: discord.Interaction,
            team_name: str,
            member1: discord.Member,
            member2: discord.Member,
            member3: discord.Member | None = None,
            member4: discord.Member | None = None,
            member5: discord.Member | None = None,
            member6: discord.Member | None = None
    ):

        organizer_role = interaction.guild.get_role(
            ORGANIZER_ROLE_ID
        )

        if (
                organizer_role not in interaction.user.roles
                and not interaction.user.guild_permissions.administrator
        ):
            return await interaction.response.send_message(
                "❌ Only Organizers may use this command!",
                ephemeral=True
            )

        guild = interaction.guild

        if team_name in teams:
            return await interaction.response.send_message(
                f"❌ Team **{team_name}** already exists!",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        print(f"[TEAM DEBUG] Syncing team: {team_name}")

        # =========================================================
        # CREATE ROLE
        # =========================================================

        team_role = await guild.create_role(
            name=f"👥｜{team_name}"
        )

        no_access_category = guild.get_channel(
            TEAM_NO_ACCESS_CATEGORY_ID
        )

        # =========================================================
        # CREATE CHANNELS
        # =========================================================

        text_channel = await guild.create_text_channel(
            name=f"🤝｜team-{team_name.lower().replace(' ', '-')}",
            category=no_access_category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                )
            }
        )

        voice_channel = await guild.create_voice_channel(
            name=f"🔊・{team_name} Lounge",
            category=no_access_category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                )
            }
        )

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

        # =========================================================
        # MEMBERS
        # =========================================================

        members = [
            member1,
            member2,
            member3,
            member4,
            member5,
            member6
        ]

        members = [m for m in members if m]

        added_members = []

        for member in members:

            # Remove existing team role if any
            for role in member.roles:
                if role.name.startswith("👥｜"):
                    try:
                        await member.remove_roles(role)
                    except Exception:
                        pass

            await member.add_roles(team_role)

            added_members.append(member.id)

            print(
                f"[TEAM DEBUG] Added {member} to {team_name}"
            )

        # =========================================================
        # STORE TEAM
        # =========================================================

        teams[team_name] = {
            "name": team_name,
            "description": "Created via /syncteam",
            "size": max(len(added_members), 4),
            "password": None,
            "creator": interaction.user.id,
            "role_id": team_role.id,
            "text_id": text_channel.id,
            "voice_id": voice_channel.id,
            "members": added_members,
            "private": False
        }

        # =========================================================
        # WELCOME MESSAGE
        # =========================================================

        mentions = [
            f"<@{member_id}>"
            for member_id in added_members
        ]

        await text_channel.send(
            f"👋 Welcome to **{team_name}**!\n\n"
            f"Assigned Members:\n"
            f"{chr(10).join(mentions)}"
        )

        await interaction.followup.send(
            f"✅ Team **{team_name}** created successfully!\n"
            f"👥 Added **{len(added_members)}** member(s).\n"
            f"💬 {text_channel.mention}\n"
            f"🔊 {voice_channel.mention}",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(TeamSelector(bot))
    print("[NEEBOT CNC DEBUGGER] syncTeamSelector.seq has been initialized!")
    print("[NEEBOT CNC DEBUGGER] teamSelector.seq has been initialized!")