import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button
import datetime
import asyncio
import random
import io
import re


afk_users = {}

# ========================== ROLURI & PERMISIUNI ==========================

STAFF_CHANNEL_ID = 1503027353138499907
STAFF_MESSAGE_ID = 1503027516900901016   # <-- AICI PUI ID-UL NOU


FULL_ACCESS = [
    1456108143271608383,  # OWNER
    1456108143271608382,  # CO_OWNER
    1456108143271608391,  # GOD
    1456108143271608389,  # CO_FONDATOR
    1456108143271608385,  # DEV_BOT
    1456108143296647328,  # BOT_MASTER / DEV
]

ROLES = {
    "TESTER_HELPER": 1456108143242117132,
    "HELPER": 1456108143242117134,
    "ADMIN": 1456108143242117136,
    "CO_OWNER": 1456108143271608382,
    "OWNER": 1456108143271608383,
    "STAFF_MANAGER": 1456108143242117140,
    "VERIF_STAFF": 1456108143271608388,
    "DEV_BOT": 1456108143271608385,
    "GOD": 1456108143271608391,
    "CO_FONDATOR": 1456108143271608389,
    "BOT_MASTER": 1456108143296647328,
    "DEV": 1456108143296647328,
}

ALLOWED = {
    "warn": [
        1456108143242117132,  # TESTER_HELPER
        1456108143242117134,  # HELPER
        1456108143242117136,  # ADMIN
        1456108143271608382,  # CO_OWNER
        1456108143271608383,  # OWNER
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "mute": [
        1456108143242117134,  # HELPER
        1456108143242117136,  # ADMIN
        1456108143271608382,  # CO_OWNER
        1456108143271608383,  # OWNER
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "unmute": [
        1456108143242117136,  # ADMIN
        1456108143271608382,  # CO_OWNER
        1456108143271608383,  # OWNER
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "ban": [
        1456108143271608382,  # CO_OWNER
        1456108143271608383,  # OWNER
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "unban": [
        1456108143242117136,  # ADMIN
        1456108143271608382,  # CO_OWNER
        1456108143271608383,  # OWNER
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "kick": [
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "lock": [
        1456108143242117136,  # ADMIN
        1456108143271608382,  # CO_OWNER
        1456108143271608383,  # OWNER
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "unlock": [
        1456108143242117136,  # ADMIN
        1456108143271608382,  # CO_OWNER
        1456108143271608383,  # OWNER
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "purge_msgs": [
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "nuke": [
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],

    "giveaway": [
        1456108143242117140,  # STAFF_MANAGER
        1456108143271608388,  # VERIF_STAFF
        1456108143271608385,  # DEV_BOT
        1456108143271608391,  # GOD
        1456108143271608389,  # CO_FONDATOR
        1456108143296647328,  # BOT_MASTER / DEV
    ],
}

def has_role_permission(command_name):
    def predicate(ctx):
        user_roles = [role.id for role in ctx.author.roles]

        # ALLOWED conține direct ID-uri, deci nu mai convertim nimic
        allowed_roles = ALLOWED.get(command_name, [])

        return (
            any(rid in user_roles for rid in allowed_roles)
            or any(r in user_roles for r in FULL_ACCESS)
        )

    return commands.check(predicate)

# ========================== INTENTS & BOT SETUP ==========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# CONFIG PERSONALIZABILĂ
# ======================
WELCOME_CHANNEL_ID = 1456108144005480553
REGULAMENT_CHANNEL_ID = 1456108145855299618
ANUNTURI_CHANNEL_ID = 1456108144504733717
TICKETS_CHANNEL_ID = 1456108144831762440

SERVER_NAME = "Comunitatea lu 𝖃𝖙𝖔𝖕"
SERVER_LINK = "Comunitatea lu 𝖃𝖙𝖔𝖕"
BOT_FOOTER_NAME = "seful"

# ================= CONFIGURARE =================
TICKET_CATEGORY_ID = 1395529657796788346
LOG_CHANNEL_ID = 1503006653375840256  # <--- SCHIMBĂ CU ID-UL CANALULUI DE LOGURI
# Gradele care au voie să vadă logurile sunt de obicei cele de Admin/Manager

TICKET_ACCESS_CONFIG = {
    "General": [1456108143242117132, 1456108143242117134, 1456108143242117136, 1456108143271608382, 1456108143271608383, 456108143242117140, 1456108143271608388, 1456108143271608385, 1456108143271608391, 1456108143271608389, 1456108143296647328, 1456108143296647328],
    "Contact-Owner": [456108143242117140, 1456108143271608388, 1456108143271608385, 1456108143271608391, 1456108143271608389, 1456108143296647328, 1456108143296647328],
    "Report-Staff": [ 456108143242117140, 1456108143271608388, 1456108143271608385, 1456108143271608391, 1456108143271608389, 1456108143296647328, 1456108143296647328],
    "Bug": [456108143242117140, 1456108143271608388, 1456108143271608385, 1456108143271608391, 1456108143271608389, 1456108143296647328, 1456108143296647328],
    "Report-Player": [ 1456108143271608382, 1456108143271608383, 456108143242117140, 1456108143271608388, 1456108143271608385, 1456108143271608391, 1456108143271608389, 1456108143296647328, 1456108143296647328],
    "Unban": [1456108143242117136, 1456108143271608382, 1456108143271608383, 456108143242117140, 1456108143271608388, 1456108143271608385, 1456108143271608391, 1456108143271608389, 1456108143296647328, 1456108143296647328],
    "Donatii": [456108143242117140, 1456108143271608388, 1456108143271608385, 1456108143271608391, 1456108143271608389, 1456108143296647328, 1456108143296647328],
}

# Giveaway system
active_giveaways = {}
ended_giveaways = {}

# Moderation
appeal_links = {}

# ========== HELPER FUNCTIONS ==========

def load_giveaways():
    """Loads giveaway data from the JSON file into memory."""
    global active_giveaways
    if os.path.exists(GIVEAWAYS_FILE):
        with open(GIVEAWAYS_FILE, 'r') as f:
            try:
                data = json.load(f)
                active_giveaways = {
                    int(k): {**v, 'end_time': datetime.datetime.fromisoformat(v['end_time'])}
                    for k, v in data.items()
                }
                print(f"Loaded {len(active_giveaways)} active giveaways from {GIVEAWAYS_FILE}.")
            except (json.JSONDecodeError, KeyError):
                print(f"Warning: {GIVEAWAYS_FILE} is empty or corrupted. Starting fresh.")
                active_giveaways = {}
    else:
        print("No giveaway file found. Starting with no active giveaways.")

def save_giveaways():
    """Saves the current giveaway data from memory to the JSON file."""
    with open(GIVEAWAYS_FILE, 'w') as f:
        data_to_save = {
            k: {**v, 'end_time': v['end_time'].isoformat()}
            for k, v in active_giveaways.items()
        }
        json.dump(data_to_save, f, indent=4)

def load_ended_giveaways():
    """Loads ended giveaway data from the JSON file into memory."""
    global ended_giveaways
    if os.path.exists(ENDED_GIVEAWAYS_FILE):
        with open(ENDED_GIVEAWAYS_FILE, 'r') as f:
            try:
                data = json.load(f)
                ended_giveaways = {int(k): v for k, v in data.items()}
                print(f"Loaded {len(ended_giveaways)} ended giveaways from {ENDED_GIVEAWAYS_FILE}.")
            except (json.JSONDecodeError, KeyError):
                print(f"Warning: {ENDED_GIVEAWAYS_FILE} is empty or corrupted. Starting fresh.")
                ended_giveaways = {}
    else:
        print("No ended giveaway file found. Starting with none.")

def save_ended_giveaways():
    """Saves the current ended giveaway data from memory to the JSON file."""
    with open(ENDED_GIVEAWAYS_FILE, 'w') as f:
        data_to_save = {}
        for k, v in ended_giveaways.items():
            v_copy = v.copy()
            if 'end_time' in v_copy and isinstance(v_copy['end_time'], datetime.datetime):
                v_copy['end_time'] = v_copy['end_time'].isoformat()
            data_to_save[k] = v_copy
        json.dump(data_to_save, f, indent=4)

def format_time_delta(delta: datetime.timedelta):
    seconds = int(delta.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days > 0: parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0: parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0: parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts: parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return ", ".join(parts)

def parse_duration(duration_str: str) -> int:
    if not duration_str: raise ValueError("Duration string cannot be empty.")
    pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)')
    matches = pattern.findall(duration_str.lower())
    if not matches: raise ValueError("Invalid time format. Use units like 'y', 'w', 'd', 'h', 'm', 's'.")
    time_units = {
        'y': 31536000, 'year': 31536000, 'years': 31536000, 'mo': 2592000, 'month': 2592000,
        'months': 2592000, 'w': 604800, 'week': 604800, 'weeks': 604800, 'd': 86400,
        'day': 86400, 'days': 86400, 'h': 3600, 'hour': 3600, 'hours': 3600, 'm': 60,
        'minute': 60, 'minutes': 60, 's': 1, 'second': 1, 'seconds': 1,
    }
    total_seconds = 0
    for value, unit in matches:
        if unit not in time_units: raise ValueError(f"Unknown time unit: '{unit}'.")
        total_seconds += int(value) * time_units[unit]
    return total_seconds

async def send_dm(user, title, description, action_by, server_name):
    try:
        embed = discord.Embed(title=title, description=f"{description}\n\n**Action performed by**: {action_by}\n**Server**: {server_name}", color=discord.Color.red())
        await user.send(embed=embed)
    except discord.Forbidden:
        print(f"Could not send DM to {user.name}.")
async def update_staff_message(guild: discord.Guild):
    channel = guild.get_channel(STAFF_CHANNEL_ID)
    if channel is None:
        return

    try:
        message = await channel.fetch_message(STAFF_MESSAGE_ID)
    except discord.NotFound:
        return

    lines = []

    for title, role_key in STAFF_SECTIONS:
        role_id = ROLES.get(role_key)
        if role_id is None:
            continue

        role = guild.get_role(role_id)
        if role is None:
            continue

        members = [m for m in guild.members if role in m.roles]

        lines.append(f"**{title}**")
        if members:
            for m in members:
                lines.append(f"{m.mention}")
        else:
            lines.append("_Nimeni_")
        lines.append("")

    content = "\n".join(lines).strip()

    await message.edit(content=content)


# ==========================
# WELCOME SYSTEM
# ==========================

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1456108144005480553)
    regulamente = bot.get_channel(1456108145855299618)
    anunturi = bot.get_channel(1456108144504733717)
    tickets = bot.get_channel(1456108144831762440)

    if channel:
        embed = discord.Embed(
            title="✨ Bine ai venit pe Server! ✨",
            description=f"👋 Salut, {member.mention}!\n🔥 Bine ai venit pe **{SERVER_NAME}** 🎉",
            color=0x87CEEB
        )

        # Secțiune cu canale importante, stil Discord
        embed.add_field(
            name="📌 Nu uita să verifici:",
            value=f"""
↳ {regulamente.mention if regulamente else "#regulament"}
 ↳ {anunturi.mention if anunturi else "#anunturi"}
  ↳ {tickets.mention if tickets else "#tickets"}
            """,
            inline=False
        )

        # Avatarul noului membru
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        # IP-ul serverului
        embed.add_field(
            name="🌍 Conectează-te:",
            value=f"🔻 **{SERVER_LINK}** 🔻",
            inline=False
        )

        # Footer cu avatarul botului
        embed.set_footer(
            text=f"🤖 Welcome | {BOT_FOOTER_NAME}",
            icon_url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        )

        await channel.send(f"🎊 Salut {member.mention}, distrează-te! 🎮", embed=embed)
        
        
# ========================== STAFF AUTO-UPDATE CONFIG ==========================

STAFF_CHANNEL_ID = 1456321388347527259
STAFF_MESSAGE_ID = 1457844804904812594

STAFF_SECTIONS = [
    ("🧠 | 💻 Dev", "DEV"),
    ("💗 | 👑 GOD 👑", "GOD"),
    ("🤖 | 👨‍💻 Developer Bot", "DEV_BOT"),
    ("🧾 | - Verifica cerere staff", "VERIF_STAFF"),
    ("🧠 | 👮 Staff Manager", "STAFF_MANAGER"),
    ("🧠 | 👑 Owner", "OWNER"),
    ("🧠 | 🔱 Co owner", "CO_OWNER"),
    ("🧠 | 🧾 Admin", "ADMIN"),
    ("🧠 | 🧠 Helper", "HELPER"),
    ("🧠 | 🧠 Tester Helper", "TESTER_HELPER"),
]


# ================= ACTIUNI TICKET =================

class TicketActions(View):
    def __init__(self, creator, ticket_type):
        super().__init__(timeout=None)
        self.creator = creator
        self.ticket_type = ticket_type
        self.claimed_by = None

    @discord.ui.button(label="🖐️ Preia Ticket", style=discord.ButtonStyle.primary)
    async def claim(self, interaction: discord.Interaction, button: Button):
        allowed_roles = TICKET_ACCESS_CONFIG.get(self.ticket_type, [])
        user_roles_ids = [role.id for role in interaction.user.roles]
        
        if not any(r_id in allowed_roles for r_id in user_roles_ids) and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Nu ai permisiunea!", ephemeral=True)
            return

        if self.claimed_by:
            await interaction.response.send_message(f"⚠️ Deja preluat de {self.claimed_by.mention}", ephemeral=True)
            return

        self.claimed_by = interaction.user
        button.disabled = True
        button.label = "Preluat ✅"
        
        for role_id in allowed_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                await interaction.channel.set_permissions(role, send_messages=False, view_channel=True)
        
        await interaction.channel.set_permissions(interaction.user, send_messages=True, view_channel=True)
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"🖐️ **{interaction.user.mention}** a preluat ticketul. Restul echipei nu mai poate scrie.")

    @discord.ui.button(label="🔒 Închide", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("💾 Se generează arhiva și se închide ticketul...")
        
        # Generare Transcript (Text)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        messages = [msg async for msg in interaction.channel.history(limit=None, oldest_first=True)]
        
        transcript_text = f"--- TRANSCRIPT TICKET: {interaction.channel.name} ---\n"
        transcript_text += f"Tip: {self.ticket_type} | Deschis de: {self.creator} (ID: {self.creator.id})\n"
        transcript_text += f"Preluat de: {self.claimed_by if self.claimed_by else 'Nimeni'}\n"
        transcript_text += "-" * 50 + "\n\n"
        
        for m in messages:
            timestamp = m.created_at.strftime('%Y-%m-%d %H:%M:%S')
            transcript_text += f"[{timestamp}] {m.author}: {m.content}\n"
            if m.attachments:
                for att in m.attachments:
                    transcript_text += f"[Fisier] {att.url}\n"

        # Salvare in buffer si trimitere
        file = discord.File(io.BytesIO(transcript_text.encode()), filename=f"transcript-{interaction.channel.name}.txt")
        
        if log_channel:
            embed = discord.Embed(title="📁 Ticket Închis", color=discord.Color.red())
            embed.add_field(name="Canal", value=interaction.channel.name, inline=True)
            embed.add_field(name="Creat de", value=self.creator.mention, inline=True)
            embed.add_field(name="Preluat de", value=self.claimed_by.mention if self.claimed_by else "Nepreluat", inline=True)
            await log_channel.send(embed=embed, file=file)
        
        await interaction.channel.delete()

# [Restul codului TicketMenu și setup_ticket rămâne identic cu cel oferit de tine]
class TicketMenu(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        staff_ids = TICKET_ACCESS_CONFIG.get(ticket_type, [])
        for role_id in staff_ids:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"{ticket_type.lower()}-{interaction.user.name}",
            overwrites=overwrites,
            category=category
        )
        
        await channel.send(f"🎫 Ticket {ticket_type} - {interaction.user.mention}", view=TicketActions(interaction.user, ticket_type))
        await interaction.followup.send(f"✅ Ticket deschis: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Vreau Jocul....", emoji="🎫", style=discord.ButtonStyle.green, row=0)
    async def general(self, interaction, button): await self.create_ticket(interaction, "Vreau Jocul....")

    @discord.ui.button(label="Contact Owner", emoji="📞", style=discord.ButtonStyle.primary, row=0)
    async def owner(self, interaction, button): await self.create_ticket(interaction, "Contact-Owner")

    @discord.ui.button(label="Report Staff", emoji="🧑‍💼", style=discord.ButtonStyle.danger, row=0)
    async def rstaff(self, interaction, button): await self.create_ticket(interaction, "Report-Staff")

    @discord.ui.button(label="Bug", emoji="🐞", style=discord.ButtonStyle.secondary, row=0)
    async def bug(self, interaction, button): await self.create_ticket(interaction, "Bug")

    @discord.ui.button(label="Report Player", emoji="🎮", style=discord.ButtonStyle.danger, row=0)
    async def rplayer(self, interaction, button): await self.create_ticket(interaction, "Report-Player")

    @discord.ui.button(label="Unban", emoji="🔓", style=discord.ButtonStyle.secondary, row=1)
    async def unban(self, interaction, button): await self.create_ticket(interaction, "Unban")

    @discord.ui.button(label="Donații", emoji="💸", style=discord.ButtonStyle.primary, row=1)
    async def donatii(self, interaction, button): await self.create_ticket(interaction, "Donatii")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    embed = discord.Embed(title="🎟️ Sistem Ticket", description="Apasă un buton pentru asistență.", color=0x2ecc71)
    await ctx.send(embed=embed, view=TicketMenu())

# ========== GIVEAWAY SYSTEM (BUTTON-BASED & PERSISTENT) ==========

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Enter", style=discord.ButtonStyle.primary, emoji="🎉", custom_id="persistent_giveaway_button")
    async def enter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        giveaway_data = active_giveaways.get(interaction.message.id)
        if not giveaway_data:
            button.disabled = True
            button.label = "Ended"
            await interaction.message.edit(view=self)
            await interaction.followup.send("This giveaway has already ended or is no longer tracked.", ephemeral=True)
            return
        entrants = giveaway_data["entrants"]
        if interaction.user.id in entrants:
            await interaction.followup.send("You have already entered this giveaway!", ephemeral=True)
        else:
            entrants.append(interaction.user.id)
            save_giveaways()
            await interaction.followup.send("You have successfully entered the giveaway!", ephemeral=True)
            original_embed = interaction.message.embeds[0]
            original_embed.set_field_at(2, name="Entries", value=str(len(entrants)), inline=True)
            await interaction.message.edit(embed=original_embed)

@tasks.loop(seconds=5)
async def check_giveaways():
    await bot.wait_until_ready()
    ended_giveaway_ids_to_process = []
    for msg_id, data in list(active_giveaways.items()):
        if datetime.datetime.now(datetime.timezone.utc) >= data["end_time"]:
            try:
                channel = await bot.fetch_channel(data["channel_id"])
                message = await channel.fetch_message(msg_id)
            except (discord.NotFound, discord.Forbidden):
                ended_giveaway_ids_to_process.append(msg_id)
                continue
            
            entrants = data["entrants"]
            winner_count = data["winner_count"]
            prize = data["prize"]
            name = data["name"]
            
            result_message = ""
            end_embed = message.embeds[0]
            winner_ids = []
            
            if not entrants:
                result_message = f"The giveaway for **{prize}** has ended. No one entered. 😢"
                end_embed.description = f"**Prize:** {prize}\n\nCould not determine a winner."
                end_embed.color = discord.Color.red()
            else:
                num_to_pick = min(winner_count, len(entrants))
                winner_ids = random.sample(entrants, num_to_pick)
                winner_mentions = [f"<@{uid}>" for uid in winner_ids]
                winner_str = ", ".join(winner_mentions)
                result_message = f"Congratulations {winner_str}! You won the **{prize}**!"
                end_embed.description = f"**Prize:** {prize}\n\n**Winner(s):** {winner_str}"
                end_embed.color = discord.Color.green()
            
            data['winners'] = winner_ids # Save winners for reroll
            
            end_embed.title = f"[ENDED] {name}"
            end_embed.clear_fields()
            end_embed.add_field(name="Hosted by", value=f"<@{data['host_id']}>")
            end_embed.add_field(name="Total Entries", value=str(len(entrants)))
            end_embed.set_footer(text="Giveaway ended")
            end_embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
            
            view = GiveawayView()
            for child in view.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
                    child.label = "Ended"
            
            await message.edit(content="🎉 **GIVEAWAY ENDED** 🎉", embed=end_embed, view=view)
            await message.reply(result_message)
            
            ended_giveaway_ids_to_process.append(msg_id)

    if ended_giveaway_ids_to_process:
        for msg_id in ended_giveaway_ids_to_process:
            ended_data = active_giveaways.pop(msg_id, None)
            if ended_data:
                ended_giveaways[msg_id] = ended_data
        save_giveaways()
        save_ended_giveaways()

@bot.hybrid_command(name="giveaway-create", description="Creates a new giveaway.")
@commands.has_permissions(manage_guild=True)
@app_commands.describe(name="Title of the giveaway.", prize="What the winner(s) will get.", duration="How long it will last.", winners="Number of winners.")
async def giveaway_create(ctx: commands.Context, name: str, prize: str, duration: str, winners: int):
    await ctx.defer(ephemeral=True)
    try:
        duration_seconds = parse_duration(duration)
        if not (10 <= duration_seconds <= 60 * 60 * 24 * 30):
             await ctx.followup.send("Duration must be between 10 seconds and 30 days.", ephemeral=True)
             return
        if winners < 1:
            await ctx.followup.send("Number of winners must be at least 1.", ephemeral=True)
            return
    except ValueError as e:
        await ctx.followup.send(f"Invalid duration format: {e}", ephemeral=True)
        return
    end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration_seconds)
    end_timestamp = int(end_time.timestamp())
    embed = discord.Embed(title=name, description=f"Click the 🎉 button to enter!\n**Prize:** {prize}", color=discord.Color.purple())
    embed.add_field(name="Ends", value=f"<t:{end_timestamp}:R> (<t:{end_timestamp}:F>)", inline=False)
    embed.add_field(name="Hosted by", value=ctx.author.mention, inline=True)
    embed.add_field(name="Entries", value="0", inline=True)
    embed.add_field(name="Winners", value=f"{winners}", inline=True)
    embed.set_footer(text="Giveaway started")
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
    view = GiveawayView()
    giveaway_message = await ctx.channel.send("🎉 **GIVEAWAY** 🎉", embed=embed, view=view)
    active_giveaways[giveaway_message.id] = {
        "channel_id": ctx.channel.id, "name": name, "prize": prize, "end_time": end_time,
        "winner_count": winners, "host_id": ctx.author.id, "entrants": []
    }
    save_giveaways()
    await ctx.followup.send(f"Giveaway for '{name}' created in {ctx.channel.mention}!", ephemeral=True)

@bot.hybrid_command(name="giveaway-end", description="Prematurely ends a giveaway without a winner.")
@commands.has_permissions(manage_guild=True)
@app_commands.describe(message_id="The message ID of the giveaway to end.")
async def giveaway_end(ctx: commands.Context, message_id: str):
    await ctx.defer(ephemeral=True)
    try:
        msg_id_int = int(message_id)
    except ValueError:
        await ctx.followup.send("Please provide a valid message ID.", ephemeral=True)
        return

    if msg_id_int not in active_giveaways:
        await ctx.followup.send("This is not an active giveaway I am tracking.", ephemeral=True)
        return

    giveaway_data = active_giveaways.pop(msg_id_int)
    save_giveaways() # Save after popping

    try:
        channel = await bot.fetch_channel(giveaway_data["channel_id"])
        message = await channel.fetch_message(msg_id_int)
    except (discord.NotFound, discord.Forbidden):
        await ctx.followup.send("Giveaway ended and removed from tracking, but I could not edit the original message.", ephemeral=True)
        return

    end_embed = message.embeds[0]
    name = giveaway_data["name"]
    prize = giveaway_data["prize"]
    end_embed.title = f"[ENDED] {name}"
    end_embed.description = f"**Prize:** {prize}\n\nThis giveaway was ended manually. No winner was chosen."
    end_embed.color = discord.Color.dark_grey()
    end_embed.clear_fields()
    end_embed.add_field(name="Hosted by", value=f"<@{giveaway_data['host_id']}>")
    end_embed.add_field(name="Total Entries", value=str(len(giveaway_data['entrants'])))
    end_embed.set_footer(text=f"Giveaway ended")
    end_embed.timestamp = discord.utils.utcnow()

    view = GiveawayView()
    for child in view.children:
        if isinstance(child, discord.ui.Button):
            child.disabled = True
            child.label = "Ended"
    await message.edit(content="🎉 **GIVEAWAY ENDED** 🎉", embed=end_embed, view=view)
    await ctx.followup.send("The giveaway has been successfully ended.", ephemeral=True)


# --- NEW COMMAND ---
@bot.hybrid_command(name="giveaway-reroll", description="Rerolls an ended giveaway to find a new winner.")
@commands.has_permissions(manage_guild=True)
@app_commands.describe(message_id="The message ID of the giveaway to reroll.")
async def giveaway_reroll(ctx: commands.Context, message_id: str):
    await ctx.defer(ephemeral=True)
    try:
        msg_id_int = int(message_id)
    except ValueError:
        await ctx.followup.send("Please provide a valid message ID.", ephemeral=True)
        return

    if msg_id_int in active_giveaways:
        await ctx.followup.send("This giveaway has not ended yet. Please end it first or wait for it to finish.", ephemeral=True)
        return

    giveaway_data = ended_giveaways.get(msg_id_int)
    if not giveaway_data:
        await ctx.followup.send("I could not find a record of this ended giveaway. The ID may be incorrect or it ended before rerolls were tracked.", ephemeral=True)
        return
        
    entrants = giveaway_data.get("entrants", [])
    if not entrants:
        await ctx.followup.send("There were no entrants in this giveaway to reroll from.", ephemeral=True)
        return
        
    original_winners = giveaway_data.get("winners", [])
    
    eligible_entrants = [entrant for entrant in entrants if entrant not in original_winners]
    
    if not eligible_entrants:
        await ctx.followup.send("No other participants are available to be chosen as a new winner.", ephemeral=True)
        return
        
    new_winner_id = random.choice(eligible_entrants)
    
    giveaway_data.setdefault("winners", []).append(new_winner_id)
    save_ended_giveaways() # Update the file with the new winner
    
    prize = giveaway_data.get("prize", "the prize")
    
    try:
        channel = await bot.fetch_channel(giveaway_data["channel_id"])
        original_message = await channel.fetch_message(msg_id_int)
        
        announcement = (
            f"🎉 **Giveaway Reroll** 🎉\n"
            f"Congratulations <@{new_winner_id}>! You are the new winner of the **{prize}**!\n"
            f"(Rerolled by {ctx.author.mention})"
        )
        await original_message.reply(announcement)
        await ctx.followup.send(f"Successfully rerolled and announced <@{new_winner_id}> as the new winner in {channel.mention}.", ephemeral=True)
        
    except (discord.NotFound, discord.Forbidden):
        await ctx.followup.send(f"I found a new winner (<@{new_winner_id}>), but I couldn't announce it in the original channel. Please check my permissions.", ephemeral=True)

#========== UTILITY & FUN COMMANDS ==========

@bot.hybrid_command(name="afk", description="Set your AFK status.")
@app_commands.describe(reason="The reason for being away.")
async def afk(ctx: commands.Context, *, reason: str = "No reason provided"):
    user_id = ctx.author.id
    afk_users[user_id] = {"start_time": datetime.datetime.now(datetime.timezone.utc), "reason": reason}
    embed = discord.Embed(description=f"✅ **{ctx.author.mention}:** You're now AFK: `{reason}`", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.hybrid_command(name="quote", description="Creates an image quote from a replied-to message.")
async def quote(ctx: commands.Context):
    if not (ctx.message.reference and ctx.message.reference.message_id):
        await ctx.send("You need to reply to a message to use this command.", ephemeral=True)
        return
    await ctx.defer()
    try:
        original_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        author = original_message.author
        async with aiohttp.ClientSession() as session:
            async with session.get(author.display_avatar.replace(size=512).url) as resp:
                if resp.status != 200:
                    await ctx.send("Could not download the user's avatar.", ephemeral=True)
                    return
                avatar_data = io.BytesIO(await resp.read())
        pfp = Image.open(avatar_data).convert("RGBA").resize((400, 400))
        base = Image.new("RGBA", (900, 400), (0, 0, 0, 255))
        base.paste(pfp, (0, 0))
        gradient = Image.new("L", (150, 400))
        for x in range(150):
            gradient.putpixel((x, 0), int(255 * (1 - (x / 150))))
        gradient_row = gradient.crop((0, 0, 150, 1))
        for y in range(400):
            gradient.paste(gradient_row, (0, y))
        shadow = Image.new("RGBA", (150, 400), (0, 0, 0, 255))
        shadow.putalpha(gradient)
        base.paste(shadow, (325, 0), shadow)
        draw = ImageDraw.Draw(base)
        try:
            main_font = ImageFont.truetype("font.ttf", 36)
            sub_font = ImageFont.truetype("font.ttf", 24)
        except IOError:
            await ctx.send("`font.ttf` not found. Please add it to the bot's directory.", ephemeral=True)
            return
        message_text = original_message.content or " "
        display_name_text = f"- {author.display_name}"
        username_text = f"@{author.name}"
        text_x = 420
        draw.text((text_x, 150), message_text, font=main_font, fill=(255, 255, 255, 255))
        draw.text((text_x, 210), display_name_text, font=sub_font, fill=(200, 200, 200, 255))
        draw.text((text_x, 240), username_text, font=sub_font, fill=(150, 150, 150, 255))
        with io.BytesIO() as buffer:
            base.save(buffer, "PNG")
            buffer.seek(0)
            await ctx.send(file=discord.File(fp=buffer, filename="quote.png"))
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
    except discord.NotFound:
        await ctx.send("I couldn't find the message you replied to.", ephemeral=True)
    except Exception as e:
        print(f"Error in imagequote: {e}")
        await ctx.send(f"An error occurred while creating the image quote.", ephemeral=True)

@bot.hybrid_command(name="scream", description="Sends a scream GIF")
async def scream(ctx: commands.Context):
    await ctx.send("https://tenor.com/view/slendy-tubbies-teletubbies-tinky-winky-po-gif-25289375")

@bot.hybrid_command(name="throw", description="Sends a throw up GIF")
async def throw(ctx: commands.Context):
    await ctx.send("https://tenor.com/view/kitty-puke-puke-vomit-kitty-vomit-cat-vomit-gif-10902081098279086080")

@bot.hybrid_command(name="lick", description="Sends a lick GIF")
async def lick(ctx: commands.Context):
    await ctx.send("https://tenor.com/view/stitch-licks-slime-gif-7826310196799265789")


# ========== MODERATION & OTHER COMMANDS ==========

@bot.hybrid_command(name="set_appeal_ban_link", description="Sets the appeal link for bans in this server.")
@commands.has_permissions(manage_guild=True)
async def set_appeal_ban_link(ctx: commands.Context, link: str):
    if not link.startswith("http://") and not link.startswith("https://"):
        await ctx.send("Please provide a valid link.", ephemeral=True)
        return
    appeal_links[ctx.guild.id] = link
    await ctx.send(f"✅ The appeal link for this server has been set to: <{link}>", ephemeral=True)

@bot.hybrid_command(name="appeal", description="Get the appeal link for this server.")
async def appeal(ctx: commands.Context):
    appeal_link = appeal_links.get(ctx.guild.id)
    if appeal_link:
        try:
            dm_message = f"Hello! Here is the appeal link for **{ctx.guild.name}**:\n{appeal_link}"
            await ctx.author.send(dm_message)
            await ctx.send("I've sent the appeal link to your DMs!", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("I couldn't send you a DM. Please check your privacy settings.", ephemeral=True)
    else:
        await ctx.send("No appeal link has been set for this server yet.", ephemeral=True)

@bot.hybrid_command(name="lock", description="Lock the channel so no one can send messages")
@commands.has_permissions(manage_channels=True)
async def lock(ctx: commands.Context):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"{ctx.channel.mention} is now locked.", ephemeral=True)

@bot.hybrid_command(name="unlock", description="Unlock the channel")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx: commands.Context):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"{ctx.channel.mention} is now unlocked.", ephemeral=True)

@bot.hybrid_command(name="nuke", description="Delete all messages from the channel")
@commands.has_permissions(manage_channels=True)
async def nuke(ctx: commands.Context):
    await ctx.defer(ephemeral=True)
    cloned_channel = await ctx.channel.clone(reason="Nuke command")
    await ctx.channel.delete()
    await cloned_channel.send(f"This channel has been nuked by {ctx.author.mention}.")

@bot.hybrid_command(name="purge_msgs", description="Delete a number of messages (max 1000)")
@commands.has_permissions(manage_messages=True)
async def purge_msgs(ctx: commands.Context, amount: int):
    if amount < 1 or amount > 1000:
        await ctx.send("Please specify between 1 and 1000 messages.", ephemeral=True)
        return
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages!", ephemeral=True)

@bot.hybrid_command(name="ban", description="Bans a user with a custom notification DM.")
@commands.has_permissions(ban_members=True)
async def ban(ctx: commands.Context, member: discord.Member, duration: str, *, reason: str):
    if member == ctx.author or member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("You cannot ban this member.", ephemeral=True)
        return
    try:
        time_seconds = parse_duration(duration)
    except ValueError as e:
        await ctx.send(str(e), ephemeral=True)
        return
        
    moderator = ctx.author
    embed = discord.Embed(title="Banned", color=discord.Color.red(), timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.add_field(name="You have been banned in", value=f"{ctx.guild.name} 🩸", inline=False)
    embed.add_field(name="Moderator", value=moderator.display_name, inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)

    if time_seconds > 0:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=time_seconds)
        embed.add_field(name="Duration", value=f"{duration} (expires <t:{int(expires_at.timestamp())}:R>)", inline=False)
    else:
        embed.add_field(name="Duration", value="Permanent", inline=False)
    
    appeal_link = appeal_links.get(ctx.guild.id)
    if appeal_link:
        embed.add_field(name="You Can Appeal Here", value=f"[Click Here to Appeal]({appeal_link})", inline=False)
    else:
        embed.add_field(name="Appeal", value="No Link Has Been Set", inline=False)

    if moderator.display_avatar:
        embed.set_thumbnail(url=moderator.display_avatar.url)
    
    dm_sent_message = ""
    try:
        await member.send(embed=embed)
        dm_sent_message = "The user has been notified via DM."
    except discord.Forbidden:
        dm_sent_message = "Could not send a DM to the user."
        
    try:
        await member.ban(reason=f"Banned by {moderator.name}. Reason: {reason}")
        await ctx.send(f"✅ Successfully banned {member.mention} for **{duration}**. {dm_sent_message}")
    except discord.Forbidden:
        await ctx.send("I do not have the permissions to ban this member.", ephemeral=True)
        return
        
    if time_seconds > 0:
        await asyncio.sleep(time_seconds)
        try:
            await ctx.guild.unban(member, reason="Temporary ban expired.")
        except (discord.NotFound, discord.Forbidden):
            pass

@bot.hybrid_command(name="kick", description="Kicks a user with a custom notification DM.")
@commands.has_permissions(kick_members=True)
async def kick(ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
    if member == ctx.author or member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("You cannot kick this member.", ephemeral=True)
        return
    await member.kick(reason=reason)
    await ctx.send(f"✅ Successfully kicked {member.mention}.")

@bot.hybrid_command(name="mute", description="Times out a member with a custom notification DM.")
@commands.has_permissions(moderate_members=True)
async def mute(ctx: commands.Context, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
    if member == ctx.author or member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("You cannot mute this member.", ephemeral=True)
        return
    try:
        time_seconds = parse_duration(duration)
        delta = datetime.timedelta(seconds=time_seconds)
        if delta.days > 28:
            await ctx.send("The maximum timeout duration is 28 days.", ephemeral=True)
            return
    except ValueError as e:
        await ctx.send(str(e), ephemeral=True)
        return
    await member.timeout(delta, reason=reason)
    await ctx.send(f"✅ Successfully timed out {member.mention} for **{duration}**.")
        
@bot.hybrid_command(name="unmute", description="Removes the timeout from a member.")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
    if member.timed_out_until is None:
        await ctx.send(f"{member.mention} is not currently timed out.", ephemeral=True)
        return
    await member.timeout(None, reason=reason)
    await ctx.send(f"✅ Successfully unmuted {member.mention}.")

@bot.hybrid_command(name="warn", description="Warns a user with a custom notification DM.")
@commands.has_permissions(administrator=True)
async def warn(ctx: commands.Context, member: discord.Member, *, reason: str):
    await ctx.send(f"✅ Successfully warned {member.mention}.")

@bot.hybrid_command(name="unban", description="Unban a user")
@commands.has_permissions(ban_members=True)
async def unban(ctx: commands.Context, user: discord.User, reason: str):
    try:
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"{user} has been unbanned.")
    except discord.NotFound:
        await ctx.send("User not found in the ban list.", ephemeral=True)

@bot.hybrid_command(name="announce", description="Send an announcement to all members via DM")
@commands.has_permissions(administrator=True)
async def announce(ctx: commands.Context, *, message: str):
    await ctx.defer(ephemeral=True)
    await ctx.followup.send("Announcement sent.", ephemeral=True)

# ========== INIT STAFF (FINAL, CORECT) ==========

@bot.hybrid_command(name="init_staff", description="Initialize staff message")
@commands.is_owner()
async def init_staff(ctx):
    msg = await ctx.channel.send("Se încarcă staff-ul...")
    await ctx.send(f"Mesajul de staff a fost creat. ID-ul lui este: `{msg.id}`", ephemeral=True)
    print(f"STAFF_MESSAGE_ID NOU: {msg.id}")

# ========== BOT EVENTS ==========

@bot.event
async def on_member_update(before, after):
    before_roles = {r.id for r in before.roles}
    after_roles = {r.id for r in after.roles}

    if before_roles == after_roles:
        return

    staff_role_ids = set(ROLES.values())

    if before_roles & staff_role_ids != after_roles & staff_role_ids:
        await update_staff_message(after.guild)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.webhook_id:
        return

    # --- USER RETURNS FROM AFK ---
    if message.author.id in afk_users:
        afk_data = afk_users.pop(message.author.id)
        start_time = afk_data["start_time"]
        duration = datetime.datetime.now(datetime.timezone.utc) - start_time

        embed = discord.Embed(
            description=f"👋 **{message.author.mention}**, welcome back! You were AFK for **{format_time_delta(duration)}**.",
            color=discord.Color.blue()
        )

        await message.channel.send(embed=embed, delete_after=10)
        await bot.process_commands(message)
        return

    # --- USER MENTIONS SOMEONE WHO IS AFK ---
    afk_mentioned_user = None

    for user in message.mentions:
        if user.id in afk_users:
            afk_mentioned_user = user
            break

    # (restul codului tău AFK aici...)

    await bot.process_commands(message)

# ==========================
# ON READY
# ==========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'✅ Logat ca {bot.user.name}')
    print("Slash commands synced.")

    # Actualizează automat mesajul staff la pornirea botului
    for guild in bot.guilds:
        await update_staff_message(guild)

# ==========================
# RUN BOT
# ==========================
bot.run("")
