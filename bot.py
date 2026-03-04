import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import asyncio
import aiohttp
import re

# =========================
# TOKEN FROM RENDER ENV
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
BANNER_FILE = "banner.png"
EMBED_COLOR = discord.Color.from_str("#501e78")

# =========================
# CHANNEL EMBED CONTENT
# =========================
CHANNEL_EMBEDS = {
    "verification":      "✅ React below to verify yourself and gain access to the server!",
    "welcome":           "👋 Welcome to **{.Σ} .ΣXΣ AUDIOS**!\n\nBefore anything else, head over to the rules channel and give them a read. We keep this server clean and fun for everyone — knowing the rules is step one.\n\nOnce you're verified, you'll unlock the full server. We're glad you're here! 🎉",
    "rules":             "**{.Σ} .ΣXΣ AUDIOS — SERVER RULES**\n\n> Follow these rules at all times. Breaking them will result in a warning, mute, kick, or ban depending on severity.\n\n**1.** Respect everyone — no harassment, hate speech, or toxicity.\n**2.** No NSFW content of any kind.\n**3.** No spamming or flooding channels.\n**4.** No advertising without permission from staff.\n**5.** Follow Discord's Terms of Service at all times.\n**6.** Listen to staff — their word is final.\n**7.** Keep content in the correct channels.\n**8.** No sharing personal information of others.\n**9.** Have fun and be a good community member! ✅",
    "announcements":     "📣 Important announcements from staff will be posted here. Stay up to date!",
    "updates":           "🔔 Game, server, and project updates are posted here. Check back often!",
    "roblox-group":      "🎮 Our official Roblox group link is pinned here. Join to get exclusive in-game perks!",
    "game-links":        "🕹️ Links to all of our Roblox games are pinned here. Jump in and play!",
    "my-profile":        "👤 Links to our creator's Roblox profile and social pages are pinned here.",
    "youtube-links":     "▶️ Our YouTube videos and content drops are linked here. Go watch and subscribe!",
    "server-partnerships": "🤝 Official server partnerships are listed here. Check out our partner servers!",
    "general":           "💬 The main hangout spot. Talk about anything and everything here!",
    "memes":             "😂 Post the funniest memes you find. Keep it appropriate!",
    "polls":             "📊 Community polls are posted here. Vote and make your voice heard!",
    "questions":         "❓ Have a question about the server, game, or community? Ask here!",
    "hall-of-shame":     "😬 Post your most embarrassing moments, worst fails, and biggest L's here. Keep it fun, not personal attacks!",
    "bot-commands":      "🤖 Use all bot commands in this channel to keep other channels clean.",
    "community-codes":   "🎁Got any codes You want to share with our community? Post them here.",
    "joins":             "📥 Member join logs are recorded here automatically.",
    "leaves":            "📤 Member leave logs are recorded here automatically.",
    "roblox-chat":       "🎮 Talk about Roblox games, updates, and anything Roblox related here!",
    "looking-to-play":   "🕹️ Looking for someone to play with? Post here and find a squad!",
    "photos":            "📷 Share your photos and screenshots here. Keep it family friendly!",
    "videos":            "🎥 Post your videos and clips here. Only share original or credited content.",
    "clips":             "✂️ Share short clips from games, streams, or anything cool here.",
    "artwork":           "🎨 Share your original artwork, fan art, and creative designs here.",
    "music":             "🎵 Share music you love or your own tracks here. Keep it chill!",
    "selfies":           "🤳 Share your selfies here! Be kind and hype each other up.",
    "edits":             "✨ Show off your photo and video edits here. Tag the tools you used!",
    "stream-highlights": "📡 Best moments from streams go here. Clips, timestamps — share it all!",
    "staff-chat":        "🛡️ Staff only chat. Keep discussions professional and on-topic.",
    "mod-logs":          "📋 Automated moderation logs are recorded here.",
    "admin-only":        "⚙️ Admin-only channel for important decisions and high-level management.",
    "private-bot-cmds":  "🤖 Private channel for owner bot commands only.",
    "logs":              "📋 Server logs are recorded here automatically.",
}

# Suggestions forum format guide shown as the first post in the forum
SUGGESTIONS_GUIDE = """ **📌 READ BEFORE POSTING — FORMAT**
Before posting, make sure your suggestion follows this format:
**Title:** Give your suggestion a short, clear title.
**Description:**
A clear explanation of your suggestion. What is it? How would it work?
**Why it would help:**
Why should we add this? How does it benefit the server or community?
**Examples (optional):**
Any examples, references, or screenshots that help explain your idea.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 **DO:**
- Be specific and detailed
- Keep it respectful and constructive
- Check if your suggestion already exists before posting
 **DON'T:**
- Post duplicate suggestions
- Be rude or dismissive of others' ideas
- Post anything unrelated to the server or community
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All suggestions are reviewed by staff. We appreciate every idea! """

# =========================
# HELPER: FIND CHANNEL BY NAME
# =========================
def find_channel(guild, name):
    for ch in guild.text_channels:
        if ch.name == name:
            return ch
    return None

# =========================
# KEEP ALIVE WEB SERVER
# =========================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive"

@app.route('/health')
def health():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

# =========================
# ROBLOX API HELPERS
# =========================
async def fetch_roblox_game(universe_id):
    """Fetch game details from Roblox Games API."""
    url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    games = data.get("data", [])
                    return games[0] if games else None
    except Exception as e:
        print(f"[Roblox API] fetch_roblox_game error: {e}")
    return None

async def fetch_roblox_thumbnail(universe_id):
    """Fetch game thumbnail URL from Roblox Thumbnails API."""
    url = (
        f"https://thumbnails.roblox.com/v1/games/icons"
        f"?universeIds={universe_id}&returnPolicy=PlaceHolder&size=512x512&format=Png&isCircular=false"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("data", [])
                    if items:
                        return items[0].get("imageUrl")
    except Exception as e:
        print(f"[Roblox API] fetch_roblox_thumbnail error: {e}")
    return None

async def fetch_roblox_game_banner(universe_id):
    """Fetch game banner/thumbnail URL (large) from Roblox Thumbnails API."""
    url = (
        f"https://thumbnails.roblox.com/v1/games/game-thumbnails"
        f"?universeIds={universe_id}&countPerUniverse=1&defaults=true&size=768x432&format=Png&isCircular=false"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("data", [])
                    if items:
                        thumbnails = items[0].get("thumbnails", [])
                        if thumbnails:
                            return thumbnails[0].get("imageUrl")
    except Exception as e:
        print(f"[Roblox API] fetch_roblox_game_banner error: {e}")
    return None

async def fetch_universe_id(place_id):
    """Convert a Roblox place ID to a universe ID."""
    url = f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("universeId")
    except Exception as e:
        print(f"[Roblox API] fetch_universe_id error: {e}")
    return None

async def fetch_roblox_user(user_id):
    """Fetch a Roblox user's profile info."""
    url = f"https://users.roblox.com/v1/users/{user_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        print(f"[Roblox API] fetch_roblox_user error: {e}")
    return None

async def fetch_roblox_avatar(user_id):
    """Fetch a Roblox user's avatar headshot URL."""
    url = (
        f"https://thumbnails.roblox.com/v1/users/avatar-headshot"
        f"?userIds={user_id}&size=420x420&format=Png&isCircular=false"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("data", [])
                    if items:
                        return items[0].get("imageUrl")
    except Exception as e:
        print(f"[Roblox API] fetch_roblox_avatar error: {e}")
    return None

async def fetch_roblox_group(group_id):
    """Fetch a Roblox group's info."""
    url = f"https://groups.roblox.com/v1/groups/{group_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        print(f"[Roblox API] fetch_roblox_group error: {e}")
    return None

async def fetch_roblox_group_icon(group_id):
    """Fetch a Roblox group's icon URL."""
    url = (
        f"https://thumbnails.roblox.com/v1/groups/icons"
        f"?groupIds={group_id}&size=420x420&format=Png&isCircular=false"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("data", [])
                    if items:
                        return items[0].get("imageUrl")
    except Exception as e:
        print(f"[Roblox API] fetch_roblox_group_icon error: {e}")
    return None

# =========================
# HELPER: SEND BANNER
# =========================
async def send_banner(channel):
    await channel.send(file=discord.File(BANNER_FILE))

# =========================
# HELPER: SEND CHANNEL EMBED
# Handles generic channels AND special Roblox-rich channels.
# =========================
async def send_channel_embed(channel, channel_key=None):
    if channel_key is None:
        channel_key = channel.name

    description = CHANNEL_EMBEDS.get(channel_key, f"Welcome to {channel.name}. Keep it clean and follow the rules.")

    # Send banner first
    try:
        await send_banner(channel)
    except FileNotFoundError:
        pass

    # ── RULES ──
    if channel_key == "rules":
        embed = discord.Embed(description=description, color=EMBED_COLOR)
        await channel.send(embed=embed)

    # ── GAME LINKS ──
    elif channel_key == "game-links":
        embed = discord.Embed(description=description, color=EMBED_COLOR)
        await channel.send(embed=embed)

        # Game 1 — Patrick's Boombox Hangout (universe ID directly)
        game1 = await fetch_roblox_game("9485321544")
        thumb1 = await fetch_roblox_thumbnail("9485321544")
        banner1 = await fetch_roblox_game_banner("9485321544")
        if game1:
            e1 = discord.Embed(
                title=game1.get("name", "Unknown Game"),
                description=game1.get("description", "No description available."),
                url=f"https://www.roblox.com/games/{game1.get('rootPlaceId', '')}",
                color=EMBED_COLOR
            )
            e1.add_field(name="👥 Active Players", value=f"{game1.get('playing', 0):,}", inline=True)
            e1.add_field(name="👁️ Visits",         value=f"{game1.get('visits', 0):,}", inline=True)
            e1.add_field(name="👍 Favorites",       value=f"{game1.get('favoritedCount', 0):,}", inline=True)
            if thumb1:
                e1.set_thumbnail(url=thumb1)
            if banner1:
                e1.set_image(url=banner1)
            e1.set_footer(text="Roblox Game")
            await channel.send(embed=e1)

        # Game 2 — Custom Boombox Lab (place ID → universe ID)
        universe2 = await fetch_universe_id("117291932416578")
        if universe2:
            game2  = await fetch_roblox_game(universe2)
            thumb2 = await fetch_roblox_thumbnail(universe2)
            banner2 = await fetch_roblox_game_banner(universe2)
            if game2:
                e2 = discord.Embed(
                    title=game2.get("name", "Unknown Game"),
                    description=game2.get("description", "No description available."),
                    url="https://www.roblox.com/games/117291932416578/Custom-Boombox-Lab",
                    color=EMBED_COLOR
                )
                e2.add_field(name="👥 Active Players", value=f"{game2.get('playing', 0):,}", inline=True)
                e2.add_field(name="👁️ Visits",         value=f"{game2.get('visits', 0):,}", inline=True)
                e2.add_field(name="👍 Favorites",       value=f"{game2.get('favoritedCount', 0):,}", inline=True)
                if thumb2:
                    e2.set_thumbnail(url=thumb2)
                if banner2:
                    e2.set_image(url=banner2)
                e2.set_footer(text="Roblox Game")
                await channel.send(embed=e2)

    # ── MY PROFILE ──
    elif channel_key == "my-profile":
        embed = discord.Embed(description=description, color=EMBED_COLOR)
        await channel.send(embed=embed)

        user   = await fetch_roblox_user("1230783705")
        avatar = await fetch_roblox_avatar("1230783705")
        if user:
            profile_embed = discord.Embed(
                title=user.get("displayName", "Unknown"),
                description=user.get("description", "No bio available."),
                url="https://www.roblox.com/users/1230783705/profile",
                color=EMBED_COLOR
            )
            profile_embed.add_field(name="Username", value=f"@{user.get('name', 'Unknown')}", inline=True)
            if avatar:
                profile_embed.set_thumbnail(url=avatar)
            profile_embed.set_footer(text="Roblox Profile")
            await channel.send(embed=profile_embed)

    # ── ROBLOX GROUP ──
    elif channel_key == "roblox-group":
        embed = discord.Embed(description=description, color=EMBED_COLOR)
        await channel.send(embed=embed)

        group = await fetch_roblox_group("56408124")
        icon  = await fetch_roblox_group_icon("56408124")
        if group:
            group_embed = discord.Embed(
                title=group.get("name", "Unknown Group"),
                description=group.get("description", "No description available."),
                url="https://www.roblox.com/communities/56408124/EXE-Audios",
                color=EMBED_COLOR
            )
            group_embed.add_field(name="👥 Members", value=f"{group.get('memberCount', 0):,}", inline=True)
            if icon:
                group_embed.set_thumbnail(url=icon)
            group_embed.set_footer(text="Roblox Group")
            await channel.send(embed=group_embed)

    # ── ALL OTHER CHANNELS ──
    else:
        embed = discord.Embed(description=description, color=EMBED_COLOR)
        await channel.send(embed=embed)

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is online.")
    print(f"Guilds: {[g.name for g in bot.guilds]}")
    print(f"Member intent enabled: {bot.intents.members}")

# =========================
# MEMBER JOIN
# =========================
@bot.event
async def on_member_join(member):
    print(f"[JOIN EVENT] {member.name} joined {member.guild.name}")
    guild = member.guild

    # WELCOME CHANNEL - no banner, just player join embed
    welcome_channel = find_channel(guild, "welcome")
    if welcome_channel:
        print(f"[JOIN EVENT] Sending to welcome channel")
        embed = discord.Embed(
            title=f"👋 {member.name} just joined!",
            description=(
                f"Hey {member.mention}, welcome to **{guild.name}**! 🎉\n\n"
                f"Please read the rules and get verified to unlock the full server."
            ),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📋 Rules", value="Head to the rules channel first.", inline=True)
        embed.add_field(name="✅ Verification", value="Get verified to unlock all channels.", inline=True)
        embed.set_footer(
            text=f"Member #{guild.member_count}",
            icon_url=guild.icon.url if guild.icon else None
        )
        embed.timestamp = discord.utils.utcnow()
        await welcome_channel.send(embed=embed)
        await welcome_channel.send(DIVIDER)
    else:
        print(f"[JOIN EVENT] Welcome channel not found!")

    # JOINS CHANNEL - banner first then embed
    joins_channel = find_channel(guild, "joins")
    if joins_channel:
        print(f"[JOIN EVENT] Sending to joins channel")
        await send_banner(joins_channel)
        embed = discord.Embed(
            title=f"🎉 Welcome to {guild.name}!",
            description=f"Hey {member.mention}! We're glad you're here. Make yourself at home!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👋 You're our member #", value=str(guild.member_count), inline=True)
        embed.add_field(name="📅 Account Age", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url if guild.icon else None)
        embed.timestamp = discord.utils.utcnow()
        await joins_channel.send(embed=embed)
        await joins_channel.send(DIVIDER)
    else:
        print(f"[JOIN EVENT] Joins channel not found!")

    # LOGS CHANNEL
    logs = find_channel(guild, "logs")
    if logs:
        embed = discord.Embed(
            title="✅ Member Joined",
            description=f"{member.mention} joined the server.",
            color=discord.Color.green()
        )
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Member Count", value=str(guild.member_count), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await logs.send(embed=embed)

# =========================
# MEMBER LEAVE
# =========================
@bot.event
async def on_member_remove(member):
    print(f"[LEAVE EVENT] {member.name} left {member.guild.name}")
    guild = member.guild

    # LEAVES CHANNEL - banner first then embed
    leaves_channel = find_channel(guild, "leaves")
    if leaves_channel:
        print(f"[LEAVE EVENT] Sending to leaves channel")
        await send_banner(leaves_channel)
        embed = discord.Embed(
            title="👋 A member has left",
            description=f"**{member.name}** has left the server.",
            color=discord.Color.red()
        )
        if member.joined_at:
            embed.add_field(name="Time with us", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Members Remaining", value=str(guild.member_count), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await leaves_channel.send(embed=embed)
        await leaves_channel.send(DIVIDER)
    else:
        print(f"[LEAVE EVENT] Leaves channel not found!")

    # LOGS CHANNEL
    logs = find_channel(guild, "logs")
    if logs:
        embed = discord.Embed(
            title="❌ Member Left",
            description=f"**{member.name}** left the server.",
            color=discord.Color.red()
        )
        if member.joined_at:
            embed.add_field(name="Time with us", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Members Remaining", value=str(guild.member_count), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await logs.send(embed=embed)

# =========================
# MESSAGE DELETE LOG
# =========================
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    logs = find_channel(message.guild, "logs")
    if logs:
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"**User:** {message.author}\n**Channel:** {message.channel.mention}",
            color=discord.Color.orange()
        )
        if message.content:
            embed.add_field(name="Content", value=message.content[:1024], inline=False)
        embed.timestamp = discord.utils.utcnow()
        await logs.send(embed=embed)

# =========================
# BUILD SERVER COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def build(ctx):
    guild = ctx.guild
    await ctx.send("⚙️ Building full server setup... this will take a moment.")

    roles_to_create = {
        "{.Σ} Owner":      discord.Color.red(),
        "{.Σ} Admin":      discord.Color.dark_red(),
        "{.Σ} Moderator":  discord.Color.orange(),
        "{.Σ} Media Team": discord.Color.purple(),
        "{.Σ} VIP":        discord.Color.gold(),
        "✅ Verified":     discord.Color.green(),
        "❌ Unverified":   discord.Color.dark_gray(),
        "🎮 Gamer":        discord.Color.blue(),
        "🎵 Music Addict": discord.Color.magenta(),
        "😂 Meme Lord":    discord.Color.teal(),
        "🔥 Active":       discord.Color.brand_red(),
        "Muted":           discord.Color.dark_grey(),
    }

    created_roles = {}
    for name, color in roles_to_create.items():
        role = await guild.create_role(name=name, color=color)
        created_roles[name] = role

    owner_r      = created_roles["{.Σ} Owner"]
    admin_r      = created_roles["{.Σ} Admin"]
    mod_r        = created_roles["{.Σ} Moderator"]
    verified_r   = created_roles["✅ Verified"]
    unverified_r = created_roles["❌ Unverified"]
    ev           = guild.default_role

    def ow(read=None, send=None, history=None):
        return discord.PermissionOverwrite(
            read_messages=read,
            send_messages=send,
            read_message_history=history
        )

    # VERIFICATION
    verify_ow = {
        ev:           ow(read=False, history=False),
        unverified_r: ow(read=True, send=True, history=True),
        verified_r:   ow(read=False, history=False),
        mod_r:        ow(read=True, send=True, history=True),
        admin_r:      ow(read=True, send=True, history=True),
        owner_r:      ow(read=True, send=True, history=True),
    }
    verify_cat = await guild.create_category("{.Σ} ───── VERIFICATION ─────", overwrites=verify_ow)
    ch = await guild.create_text_channel("verification", category=verify_cat, overwrites=verify_ow)
    await send_channel_embed(ch, "verification")

    logs_ow = {
        ev:      ow(read=False, history=False),
        mod_r:   ow(read=True, send=True, history=True),
        admin_r: ow(read=True, send=True, history=True),
        owner_r: ow(read=True, send=True, history=True),
    }
    logs_cat = await guild.create_category("{.Σ} ───── LOGS ─────", overwrites=logs_ow)
    await guild.create_text_channel("logs", category=logs_cat, overwrites=logs_ow)

    # INFORMATION
    info_ow = {
        ev:         ow(read=False, send=False, history=False),
        verified_r: ow(read=True, send=False, history=True),
        mod_r:      ow(read=True, send=True, history=True),
        admin_r:    ow(read=True, send=True, history=True),
        owner_r:    ow(read=True, send=True, history=True),
    }
    info_cat = await guild.create_category("{.Σ} ───── INFORMATION ─────", overwrites=info_ow)
    for ch_name in ["welcome", "rules", "announcements", "updates"]:
        ch = await guild.create_text_channel(ch_name, category=info_cat, overwrites=info_ow)
        await send_channel_embed(ch, ch_name)

    # LINKS
    links_ow = {
        ev:         ow(read=False, send=False, history=False),
        verified_r: ow(read=True, send=False, history=True),
        mod_r:      ow(read=True, send=True, history=True),
        admin_r:    ow(read=True, send=True, history=True),
        owner_r:    ow(read=True, send=True, history=True),
    }
    links_cat = await guild.create_category("{.Σ} ───── LINKS ─────", overwrites=links_ow)
    for ch_name in ["roblox-group", "game-links", "my-profile", "youtube-links", "server-partnerships"]:
        ch = await guild.create_text_channel(ch_name, category=links_cat, overwrites=links_ow)
        await send_channel_embed(ch, ch_name)

    # COMMUNITY
    community_ow = {
        ev:         ow(read=False, history=False),
        verified_r: ow(read=True, send=True, history=True),
        mod_r:      ow(read=True, send=True, history=True),
        admin_r:    ow(read=True, send=True, history=True),
        owner_r:    ow(read=True, send=True, history=True),
    }
    community_readonly_ow = {
        ev:         ow(read=False, send=False, history=False),
        verified_r: ow(read=True, send=False, history=True),
        mod_r:      ow(read=True, send=True, history=True),
        admin_r:    ow(read=True, send=True, history=True),
        owner_r:    ow(read=True, send=True, history=True),
    }
    community_cat = await guild.create_category("{.Σ} ───── COMMUNITY ─────", overwrites=community_ow)
    for ch_name in ["general", "memes", "polls", "questions", "community-codes", "joins", "leaves"]:
        ch = await guild.create_text_channel(ch_name, category=community_cat, overwrites=community_ow)
        await send_channel_embed(ch, ch_name)
    for ch_name in ["hall-of-shame", "bot-commands"]:
        ch = await guild.create_text_channel(ch_name, category=community_cat, overwrites=community_readonly_ow)
        await send_channel_embed(ch, ch_name)

    # SUPPORT
    support_ow = {
        ev:         ow(read=False, history=False),
        verified_r: ow(read=True, send=True, history=True),
        mod_r:      ow(read=True, send=True, history=True),
        admin_r:    ow(read=True, send=True, history=True),
        owner_r:    ow(read=True, send=True, history=True),
    }
    support_cat = await guild.create_category("{.Σ} ───── SUPPORT ─────", overwrites=support_ow)

    for ch_name in ["roblox-chat", "looking-to-play"]:
        ch = await guild.create_text_channel(ch_name, category=support_cat, overwrites=support_ow)
        await send_channel_embed(ch, ch_name)

    # Suggestions forum channel
    suggestions_ow = {
        ev:           discord.PermissionOverwrite(
            read_messages=False,
            read_message_history=False,
            send_messages=False,
            create_public_threads=False,
            use_application_commands=False
        ),
        unverified_r: discord.PermissionOverwrite(
            read_messages=False,
            read_message_history=False,
            send_messages=False,
            create_public_threads=False
        ),
        verified_r:   discord.PermissionOverwrite(
            read_messages=True,
            read_message_history=True,
            send_messages=True,
            create_public_threads=True,
            use_application_commands=True
        ),
        mod_r:        discord.PermissionOverwrite(
            read_messages=True,
            read_message_history=True,
            send_messages=True,
            manage_messages=True,
            manage_threads=True,
            create_public_threads=True
        ),
        admin_r:      discord.PermissionOverwrite(
            read_messages=True,
            read_message_history=True,
            send_messages=True,
            manage_messages=True,
            manage_threads=True,
            create_public_threads=True
        ),
        owner_r:      discord.PermissionOverwrite(
            read_messages=True,
            read_message_history=True,
            send_messages=True,
            manage_messages=True,
            manage_threads=True,
            create_public_threads=True
        ),
    }

    suggestions_ch = await guild.create_forum(
        "suggestions",
        category=support_cat,
        topic="Got an idea? Post it here using the format guide pinned at the top!",
        overwrites=suggestions_ow,
        available_tags=[
            discord.ForumTag(name="💡 Idea"),
            discord.ForumTag(name="🎮 Game"),
            discord.ForumTag(name="🛡️ Server"),
            discord.ForumTag(name="🤖 Bot"),
            discord.ForumTag(name="✅ Approved"),
            discord.ForumTag(name="❌ Denied"),
            discord.ForumTag(name="👀 Under Review"),
        ]
    )
    sug_embed = discord.Embed(description=SUGGESTIONS_GUIDE, color=EMBED_COLOR)
    sug_embed.set_image(url="attachment://banner.png")
    try:
        sug_file = discord.File(BANNER_FILE, filename="banner.png")
        await suggestions_ch.create_thread(
            name="📋 READ BEFORE POSTING — Suggestion Format Guide",
            embed=sug_embed,
            file=sug_file,
            auto_archive_duration=10080,
        )
    except FileNotFoundError:
        await suggestions_ch.create_thread(
            name="📋 READ BEFORE POSTING — Suggestion Format Guide",
            embed=sug_embed,
            auto_archive_duration=10080,
        )

    # MEDIA ZONE
    media_ow = {
        ev:         ow(read=False, history=False),
        verified_r: ow(read=True, send=True, history=True),
        mod_r:      ow(read=True, send=True, history=True),
        admin_r:    ow(read=True, send=True, history=True),
        owner_r:    ow(read=True, send=True, history=True),
    }
    media_cat = await guild.create_category("{.Σ} ───── MEDIA ZONE ─────", overwrites=media_ow)
    for ch_name in ["photos", "videos", "clips", "artwork", "music", "selfies", "edits", "stream-highlights"]:
        ch = await guild.create_text_channel(ch_name, category=media_cat, overwrites=media_ow)
        await send_channel_embed(ch, ch_name)

    # STAFF
    staff_ow = {
        ev:      ow(read=False, history=False),
        mod_r:   ow(read=True, send=True, history=True),
        admin_r: ow(read=True, send=True, history=True),
        owner_r: ow(read=True, send=True, history=True),
    }
    staff_cat = await guild.create_category("{.Σ} ───── STAFF ─────", overwrites=staff_ow)
    for ch_name in ["staff-chat", "mod-logs", "admin-only", "private-bot-cmds"]:
        ch = await guild.create_text_channel(ch_name, category=staff_cat, overwrites=staff_ow)
        await send_channel_embed(ch, ch_name)

    await ctx.send("✅ Full server setup complete!")

# =========================
# WIPE SERVER COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def wipe(ctx):
    await ctx.send("⚠️ Type CONFIRM to wipe the entire server.")

    def check(m):
        return m.author == ctx.author and m.content == "CONFIRM"

    try:
        await bot.wait_for("message", timeout=20, check=check)
    except:
        await ctx.send("❌ Cancelled.")
        return

    guild = ctx.guild
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            pass
    for role in guild.roles:
        if role.name != "@everyone" and not role.managed:
            try:
                await role.delete()
            except:
                pass
    await ctx.send("💀 Server wiped.")

# =========================
# UPDATE CHANNEL COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def updatechan(ctx, channel: discord.TextChannel):
    msg = await ctx.send(f"🔄 Updating {channel.mention}...")
    try:
        deleted = await channel.purge(limit=None)
        if channel.category:
            await channel.edit(sync_permissions=True)
        ch_key = channel.name
        if ch_key not in CHANNEL_EMBEDS:
            await msg.edit(content=f"⚠️ Cleared {channel.mention} ({len(deleted)} messages) but `{ch_key}` has no entry in CHANNEL_EMBEDS.")
            return
        await send_channel_embed(channel, ch_key)
        await msg.edit(content=f"✅ {channel.mention} updated! ({len(deleted)} old messages cleared)")
    except Exception as e:
        await msg.edit(content=f"❌ Error: {str(e)}")

# =========================
# FIX PERMISSIONS COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def fixperms(ctx, *, target=None):
    if not target:
        await ctx.send("❌ Usage: `!fixperms #channel`, `!fixperms category_name`, or `!fixperms all`")
        return

    unverified_r = discord.utils.get(ctx.guild.roles, name="❌ Unverified")
    if not unverified_r:
        await ctx.send("❌ Could not find '❌ Unverified' role!")
        return

    msg = await ctx.send("🔄 Fixing permissions...")
    fixed_count = 0

    if ctx.message.channel_mentions:
        ch = ctx.message.channel_mentions[0]
        try:
            await ch.set_permissions(ctx.guild.default_role, read_messages=True, read_message_history=True)
            await ch.set_permissions(unverified_r, read_messages=False, read_message_history=False)
            if ch.name in ["welcome", "verification"]:
                await ch.set_permissions(unverified_r, read_messages=True, read_message_history=True)
            await msg.edit(content=f"✅ Fixed permissions for {ch.mention}")
        except Exception as e:
            await msg.edit(content=f"❌ Error: {str(e)}")
        return

    target = target.lower()
    cats_to_fix = ["links", "information", "community", "verification", "support", "media"] if target == "all" else [target]

    for cat in ctx.guild.categories:
        if any(c in cat.name.lower() for c in cats_to_fix):
            for ch in cat.channels:
                try:
                    await ch.set_permissions(ctx.guild.default_role, read_messages=True, read_message_history=True)
                    await ch.set_permissions(unverified_r, read_messages=False, read_message_history=False)
                    if ch.name in ["welcome", "verification"]:
                        await ch.set_permissions(unverified_r, read_messages=True, read_message_history=True)
                    fixed_count += 1
                except Exception as e:
                    print(f"Error fixing {ch.name}: {e}")

    await msg.edit(content=f"✅ Fixed permissions for {fixed_count} channels!")

# =========================
# SCAN COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def scan(ctx):
    await ctx.send("🔍 Scanning server... This might take a minute.")
    guild = ctx.guild
    output = []

    output.append("="*50)
    output.append(f"SERVER SCAN: {guild.name}")
    output.append(f"Server ID: {guild.id}")
    output.append(f"Owner: {guild.owner}")
    output.append(f"Member Count: {guild.member_count}")
    output.append("="*50 + "\n")

    output.append("📋 ROLES:")
    output.append("-"*50)
    for role in guild.roles:
        output.append(f"\nRole: {role.name}")
        output.append(f"  ID: {role.id}")
        output.append(f"  Color: {role.color}")
        output.append(f"  Position: {role.position}")
        output.append(f"  Mentionable: {role.mentionable}")
        output.append(f"  Hoisted: {role.hoist}")
        output.append(f"  Managed: {role.managed}")
        output.append(f"  Permissions: {role.permissions.value}")
    output.append("\n" + "="*50 + "\n")

    output.append("📁 CATEGORIES & CHANNELS:")
    output.append("-"*50)
    for cat in guild.categories:
        output.append(f"\n📂 CATEGORY: {cat.name}")
        output.append(f"   ID: {cat.id} | Position: {cat.position}")
        for t, ow in cat.overwrites.items():
            perms = [f"{p}: {v}" for p, v in ow if v is not None]
            output.append(f"      {t.name}: {', '.join(perms)}")
        for ch in cat.channels:
            ch_type = "💬" if isinstance(ch, discord.TextChannel) else "🔊" if isinstance(ch, discord.VoiceChannel) else "📋"
            output.append(f"\n   {ch_type} {ch.name} (ID: {ch.id})")
            for t, ow in ch.overwrites.items():
                perms = [f"{p}: {v}" for p, v in ow if v is not None]
                if perms:
                    output.append(f"      {t.name}: {', '.join(perms)}")
            if isinstance(ch, discord.TextChannel):
                try:
                    msgs = [m async for m in ch.history(limit=5)]
                    if msgs:
                        output.append(f"      RECENT MESSAGES:")
                        for m in reversed(msgs):
                            if m.author.bot:
                                continue
                            content = m.content[:100] if m.content else "[embed only]"
                            output.append(f"         [{m.author.name}]: {content}")
                except:
                    output.append(f"      [Could not read messages]")

    output.append("\n" + "="*50 + "\n")
    output.append("👥 MEMBERS:")
    output.append("-"*50)
    for member in guild.members:
        output.append(f"\n{member.name} | Bot: {member.bot} | Top Role: {member.top_role.name}")
        output.append(f"  Roles: {', '.join([r.name for r in member.roles[1:]])}")

    output.append("\n" + "="*50)

    filename = f"/tmp/server_scan_{guild.id}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    private_ch = find_channel(guild, "private-bot-cmds")
    target_ch = private_ch or ctx.channel
    await target_ch.send(f"✅ Scan complete! {len(output)} lines.", file=discord.File(filename))
    if private_ch and private_ch != ctx.channel:
        await ctx.send(f"✅ Scan sent to {private_ch.mention}")

    try:
        os.remove(filename)
    except:
        pass

# =========================
# MODERATION COMMANDS
# =========================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    if amount > 100:
        await ctx.send("❌ Max 100 messages at once.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ Deleted {len(deleted)-1} messages!")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    embed = discord.Embed(
        title="👢 Member Kicked",
        description=f"**User:** {member.mention}\n**Reason:** {reason}\n**By:** {ctx.author.mention}",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    embed = discord.Embed(
        title="🔨 Member Banned",
        description=f"**User:** {member.mention}\n**Reason:** {reason}\n**By:** {ctx.author.mention}",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned **{user.name}**")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ Added {role.mention} to {member.mention}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"✅ Removed {role.mention} from {member.mention}")

# =========================
# INFO COMMANDS
# =========================
@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=EMBED_COLOR)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="💬 Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
    embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🏷️ Display Name", value=member.display_name, inline=True)
    embed.add_field(name="🆔 User ID", value=member.id, inline=True)
    embed.add_field(name="📅 Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=False)
    if member.joined_at:
        embed.add_field(name="📥 Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=False)
    roles = [r.mention for r in member.roles[1:]]
    if roles:
        embed.add_field(name=f"🎭 Roles [{len(roles)}]", value=" ".join(roles[:10]), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latency: **{round(bot.latency * 1000)}ms**")

# =========================
# BOTCOMMANDS
# =========================
@bot.command()
async def botcommands(ctx):
    embed = discord.Embed(
        title="🤖 {.Σ} Bot Commands",
        description="Here are all available commands:",
        color=EMBED_COLOR
    )
    embed.add_field(
        name="👑 Owner Only",
        value="`!build` - Build full server\n`!wipe` - Wipe server\n`!updatechan #channel` - Rebuild a channel\n`!fixperms <target>` - Fix permissions\n`!scan` - Scan server\n`!testjoin` - Test join event\n`!testleave` - Test leave event\n`!shutdown` - Shut down bot",
        inline=False
    )
    embed.add_field(
        name="🛠️ Moderation",
        value="`!clear <amount>` - Delete messages\n`!kick @user <reason>` - Kick member\n`!ban @user <reason>` - Ban member\n`!unban <user_id>` - Unban user\n`!addrole @user @role` - Add role\n`!removerole @user @role` - Remove role",
        inline=False
    )
    embed.add_field(
        name="📊 Info",
        value="`!serverinfo` - Server stats\n`!userinfo [@user]` - User info\n`!ping` - Check latency\n`!botcommands` - Show this message",
        inline=False
    )
    await ctx.send(embed=embed)



# =========================
# SMART LINK HELPERS (for !bm)
# =========================

async def fetch_discord_invite(code):
    """Fetch Discord invite info via public API."""
    url = f"https://discord.com/api/v9/invites/{code}?with_counts=true"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "DiscordBot (custom, 1.0)"}) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        print(f"[SmartEmbed] fetch_discord_invite error: {e}")
    return None

def _detect_link(text):
    """
    Returns (link_type, identifier) or (None, None).
    Types: 'roblox_game', 'roblox_user', 'roblox_group', 'discord_invite'
    identifier: the ID or invite code string
    """
    # Roblox game:  roblox.com/games/PLACEID
    m = re.search(r"roblox\.com/games/(\d+)", text, re.IGNORECASE)
    if m:
        return "roblox_game", m.group(1)

    # Roblox user:  roblox.com/users/USERID
    m = re.search(r"roblox\.com/users/(\d+)", text, re.IGNORECASE)
    if m:
        return "roblox_user", m.group(1)

    # Roblox group: roblox.com/communities/GROUPID or roblox.com/groups/GROUPID
    m = re.search(r"roblox\.com/(?:communities|groups)/(\d+)", text, re.IGNORECASE)
    if m:
        return "roblox_group", m.group(1)

    # Discord invite: discord.gg/CODE or discord.com/invite/CODE
    m = re.search(r"discord(?:\.gg|\.com/invite)/([A-Za-z0-9\-]+)", text, re.IGNORECASE)
    if m:
        return "discord_invite", m.group(1)

    return None, None


async def _build_smart_embed(link_type, identifier, original_url):
    """Build a rich embed for a detected link. Returns discord.Embed or None."""
    if link_type == "roblox_game":
        # Convert place ID to universe ID first
        universe_id = await fetch_universe_id(identifier)
        if not universe_id:
            return None
        game  = await fetch_roblox_game(universe_id)
        thumb = await fetch_roblox_thumbnail(universe_id)
        banner = await fetch_roblox_game_banner(universe_id)
        if not game:
            return None
        e = discord.Embed(
            title=game.get("name", "Unknown Game"),
            description=game.get("description", "No description available."),
            url=original_url,
            color=EMBED_COLOR
        )
        e.add_field(name="\U0001f465 Active Players", value=f"{game.get('playing', 0):,}", inline=True)
        e.add_field(name="\U0001f441\ufe0f Visits",   value=f"{game.get('visits', 0):,}", inline=True)
        e.add_field(name="\U0001f44d Favorites",      value=f"{game.get('favoritedCount', 0):,}", inline=True)
        if thumb:
            e.set_thumbnail(url=thumb)
        if banner:
            e.set_image(url=banner)
        e.set_footer(text="Roblox Game")
        return e

    elif link_type == "roblox_user":
        user   = await fetch_roblox_user(identifier)
        avatar = await fetch_roblox_avatar(identifier)
        if not user:
            return None
        e = discord.Embed(
            title=user.get("displayName", "Unknown"),
            description=user.get("description", "No bio available."),
            url=original_url,
            color=EMBED_COLOR
        )
        e.add_field(name="Username", value=f"@{user.get('name', 'Unknown')}", inline=True)
        if avatar:
            e.set_thumbnail(url=avatar)
        e.set_footer(text="Roblox Profile")
        return e

    elif link_type == "roblox_group":
        group = await fetch_roblox_group(identifier)
        icon  = await fetch_roblox_group_icon(identifier)
        if not group:
            return None
        e = discord.Embed(
            title=group.get("name", "Unknown Group"),
            description=group.get("description", "No description available."),
            url=original_url,
            color=EMBED_COLOR
        )
        e.add_field(name="\U0001f465 Members", value=f"{group.get('memberCount', 0):,}", inline=True)
        if icon:
            e.set_thumbnail(url=icon)
        e.set_footer(text="Roblox Group")
        return e

    elif link_type == "discord_invite":
        data = await fetch_discord_invite(identifier)
        if not data:
            return None
        guild_data = data.get("guild", {})
        name       = guild_data.get("name", "Unknown Server")
        desc       = guild_data.get("description") or "No description available."
        members    = data.get("approximate_member_count", 0)
        online     = data.get("approximate_presence_count", 0)
        icon_hash  = guild_data.get("icon")
        guild_id   = guild_data.get("id")
        icon_url   = f"https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.png" if icon_hash and guild_id else None
        invite_url = f"https://discord.gg/{identifier}"

        e = discord.Embed(
            title=f"\U0001f4e8 {name}",
            description=desc,
            url=invite_url,
            color=EMBED_COLOR
        )
        e.add_field(name="\U0001f465 Members", value=f"{members:,}", inline=True)
        e.add_field(name="\U0001f7e2 Online",  value=f"{online:,}", inline=True)
        if icon_url:
            e.set_thumbnail(url=icon_url)
        e.set_footer(text="Discord Server")
        return e

    return None


# =========================
# BOT MESSAGE CREATOR
# =========================
@bot.command()
@commands.is_owner()
async def bm(ctx):
    """Interactive bot message builder with 4 message types + smart link embeds."""

    TYPE_EMOJIS = ["\u0031\ufe0f\u20e3", "\u0032\ufe0f\u20e3", "\u0033\ufe0f\u20e3", "\u0034\ufe0f\u20e3"]

    async def wait_for_reply(prompt_msg, timeout=300):
        def check(m):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and m.reference is not None
                and m.reference.message_id == prompt_msg.id
            )
        try:
            reply = await bot.wait_for("message", check=check, timeout=timeout)
            return reply.content.strip(), reply
        except asyncio.TimeoutError:
            return None, None

    async def do_send(channel, msg_type, message_content, description_text=None, smart_embed=None):
        """Send the final message to the target channel."""
        # Determine the main embed to use
        def make_plain():
            return discord.Embed(description=message_content, color=EMBED_COLOR)

        main_embed = smart_embed if smart_embed else make_plain()

        if msg_type == 1:
            await channel.send(embed=main_embed)

        elif msg_type == 2:
            try:
                await channel.send(file=discord.File(BANNER_FILE))
            except FileNotFoundError:
                pass
            await channel.send(embed=discord.Embed(description=description_text, color=EMBED_COLOR))
            await channel.send(embed=main_embed)

        elif msg_type == 3:
            # Banner inside the embed as image at bottom
            # Only add set_image if smart_embed didn't already set one
            if not smart_embed:
                main_embed.set_image(url="attachment://banner.png")
            try:
                await channel.send(embed=main_embed, file=discord.File(BANNER_FILE, filename="banner.png"))
            except FileNotFoundError:
                await channel.send(embed=main_embed)

        elif msg_type == 4:
            try:
                await channel.send(file=discord.File(BANNER_FILE))
            except FileNotFoundError:
                pass
            await channel.send(embed=main_embed)

    async def do_preview(msg_type, message_content, description_text=None, smart_embed=None):
        """Send a preview into the current channel. Returns list of sent messages."""
        sent = []

        def make_plain():
            return discord.Embed(description=message_content, color=EMBED_COLOR)

        main_embed = smart_embed if smart_embed else make_plain()

        if msg_type == 1:
            sent.append(await ctx.send(embed=main_embed))

        elif msg_type == 2:
            try:
                sent.append(await ctx.send(file=discord.File(BANNER_FILE)))
            except FileNotFoundError:
                pass
            sent.append(await ctx.send(embed=discord.Embed(description=description_text, color=EMBED_COLOR)))
            sent.append(await ctx.send(embed=main_embed))

        elif msg_type == 3:
            if not smart_embed:
                main_embed.set_image(url="attachment://banner.png")
            try:
                sent.append(await ctx.send(embed=main_embed, file=discord.File(BANNER_FILE, filename="banner.png")))
            except FileNotFoundError:
                sent.append(await ctx.send(embed=main_embed))

        elif msg_type == 4:
            try:
                sent.append(await ctx.send(file=discord.File(BANNER_FILE)))
            except FileNotFoundError:
                pass
            sent.append(await ctx.send(embed=main_embed))

        return sent

    # ── STEP 1: Pick type ──
    type_desc = (
        "Which message type would you like to create?\n\n"
        "\u0031\ufe0f\u20e3 \u2014 Embed with message content only\n"
        "\u0032\ufe0f\u20e3 \u2014 Banner + description embed + message embed\n"
        "\u0033\ufe0f\u20e3 \u2014 Embed with message content + banner at bottom\n"
        "\u0034\ufe0f\u20e3 \u2014 Banner (separate) + message embed\n\n"
        "React to select a type. Session times out after **120s**."
    )
    type_embed = discord.Embed(title="\U0001f4dd Bot Message Creator", description=type_desc, color=EMBED_COLOR)
    type_msg = await ctx.send(embed=type_embed)
    for em in TYPE_EMOJIS:
        await type_msg.add_reaction(em)

    def type_check(reaction, user):
        return (
            user == ctx.author
            and reaction.message.id == type_msg.id
            and str(reaction.emoji) in TYPE_EMOJIS
        )
    try:
        reaction, _ = await bot.wait_for("reaction_add", check=type_check, timeout=120)
    except asyncio.TimeoutError:
        await type_msg.edit(embed=discord.Embed(title="\u23f0 Timed out.", color=discord.Color.orange()))
        try:
            await type_msg.clear_reactions()
        except Exception:
            pass
        return

    msg_type = TYPE_EMOJIS.index(str(reaction.emoji)) + 1
    try:
        await type_msg.clear_reactions()
    except Exception:
        pass
    await type_msg.edit(embed=discord.Embed(
        description=f"\u2705 **Type {msg_type} selected.**",
        color=EMBED_COLOR
    ))

    # ── STEP 2: Collect content ──
    description_text = None
    message_content  = None

    if msg_type == 2:
        desc_prompt = await ctx.send(embed=discord.Embed(
            description="**Reply to this message** with your **description** text.",
            color=EMBED_COLOR
        ))
        description_text, desc_reply = await wait_for_reply(desc_prompt)
        if description_text is None:
            await desc_prompt.edit(embed=discord.Embed(description="\u23f0 Timed out.", color=discord.Color.orange()))
            return
        try:
            await desc_reply.delete()
        except Exception:
            pass
        await desc_prompt.edit(embed=discord.Embed(description="\u2705 Description saved.", color=EMBED_COLOR))

        content_prompt = await ctx.send(embed=discord.Embed(
            description="**Reply to this message** with your **main message content**.",
            color=EMBED_COLOR
        ))
        message_content, content_reply = await wait_for_reply(content_prompt)
        if message_content is None:
            await content_prompt.edit(embed=discord.Embed(description="\u23f0 Timed out.", color=discord.Color.orange()))
            return
        try:
            await content_reply.delete()
        except Exception:
            pass
        await content_prompt.edit(embed=discord.Embed(description="\u2705 Message content saved.", color=EMBED_COLOR))

    else:
        content_prompt = await ctx.send(embed=discord.Embed(
            description="**Reply to this message** with your **message content**.",
            color=EMBED_COLOR
        ))
        message_content, content_reply = await wait_for_reply(content_prompt)
        if message_content is None:
            await content_prompt.edit(embed=discord.Embed(description="\u23f0 Timed out.", color=discord.Color.orange()))
            return
        try:
            await content_reply.delete()
        except Exception:
            pass
        await content_prompt.edit(embed=discord.Embed(description="\u2705 Message content saved.", color=EMBED_COLOR))

    # ── STEP 2b: Smart link detection ──
    smart_embed = None
    link_type, link_id = _detect_link(message_content)

    if link_type:
        # Extract the original URL from the content for the embed hyperlink
        url_match = re.search(
            r"https?://[^\s]+",
            message_content,
            re.IGNORECASE
        )
        original_url = url_match.group(0) if url_match else ""

        type_labels = {
            "roblox_game":    "\U0001f3ae Roblox Game",
            "roblox_user":    "\U0001f464 Roblox User Profile",
            "roblox_group":   "\U0001f465 Roblox Group",
            "discord_invite": "\U0001f4e8 Discord Server Invite",
        }
        label = type_labels.get(link_type, "Link")

        smart_detect_msg = await ctx.send(embed=discord.Embed(
            title="\u2728 Smart Embed Detected!",
            description=(
                f"Found a **{label}** link.\n\n"
                f"React \u2705 to auto-build a rich embed with live data from this link,\n"
                f"or \u274c to use plain text instead."
            ),
            color=EMBED_COLOR
        ))
        await smart_detect_msg.add_reaction("\u2705")
        await smart_detect_msg.add_reaction("\u274c")

        def smart_check(reaction, user):
            return (
                user == ctx.author
                and reaction.message.id == smart_detect_msg.id
                and str(reaction.emoji) in ["\u2705", "\u274c"]
            )
        try:
            smart_reaction, _ = await bot.wait_for("reaction_add", check=smart_check, timeout=60)
        except asyncio.TimeoutError:
            await smart_detect_msg.edit(embed=discord.Embed(
                description="\u23f0 Timed out — using plain text.",
                color=discord.Color.orange()
            ))
            smart_reaction = None

        if smart_reaction and str(smart_reaction.emoji) == "\u2705":
            building_msg = await smart_detect_msg.edit(embed=discord.Embed(
                description=f"\u23f3 Fetching data for **{label}**...",
                color=EMBED_COLOR
            ))
            try:
                await smart_detect_msg.clear_reactions()
            except Exception:
                pass
            smart_embed = await _build_smart_embed(link_type, link_id, original_url)
            if smart_embed:
                await smart_detect_msg.edit(embed=discord.Embed(
                    description=f"\u2705 Smart embed built for **{label}**!",
                    color=EMBED_COLOR
                ))
            else:
                await smart_detect_msg.edit(embed=discord.Embed(
                    description="\u26a0\ufe0f Could not fetch data \u2014 using plain text instead.",
                    color=discord.Color.orange()
                ))
        else:
            try:
                await smart_detect_msg.clear_reactions()
            except Exception:
                pass
            await smart_detect_msg.edit(embed=discord.Embed(
                description="\u2705 Using plain text embed.",
                color=EMBED_COLOR
            ))

    # ── STEP 3: Channel selection ──
    chan_desc = (
        "**Reply to this message** with the channel to send to.\n\n"
        "Type **#channel-name** to pick a channel, or **C** for the current channel."
    )
    chan_prompt = await ctx.send(embed=discord.Embed(description=chan_desc, color=EMBED_COLOR))
    chan_content, chan_reply = await wait_for_reply(chan_prompt, timeout=120)
    if chan_content is None:
        await chan_prompt.edit(embed=discord.Embed(description="\u23f0 Timed out.", color=discord.Color.orange()))
        return
    try:
        await chan_reply.delete()
    except Exception:
        pass

    if chan_content.upper() == "C":
        target_channel = ctx.channel
    elif chan_reply.channel_mentions:
        target_channel = chan_reply.channel_mentions[0]
    else:
        name = chan_content.lstrip("#").strip()
        target_channel = find_channel(ctx.guild, name)
        if not target_channel:
            await chan_prompt.edit(embed=discord.Embed(
                description="\u274c Channel not found. Mention it with **#channel-name** or type **C**.",
                color=discord.Color.red()
            ))
            return

    await chan_prompt.edit(embed=discord.Embed(
        description=f"\u2705 Channel set to {target_channel.mention}.",
        color=EMBED_COLOR
    ))

    # ── STEP 4: Preview ──
    preview_header = await ctx.send(embed=discord.Embed(
        title="\U0001f441\ufe0f This is the final draft of your message. Ready to send?",
        description=(
            f"**Sending to:** {target_channel.mention}\n\u200b\n"
            f"*(This preview is only visible here \u2014 the message has not been sent yet.)*"
        ),
        color=EMBED_COLOR
    ))
    preview_msgs = await do_preview(msg_type, message_content, description_text, smart_embed)

    confirm_msg = await ctx.send(embed=discord.Embed(
        description="React with \u2705 to **send** or \u274c to **start over**.",
        color=EMBED_COLOR
    ))
    await confirm_msg.add_reaction("\u2705")
    await confirm_msg.add_reaction("\u274c")

    def confirm_check(reaction, user):
        return (
            user == ctx.author
            and reaction.message.id == confirm_msg.id
            and str(reaction.emoji) in ["\u2705", "\u274c"]
        )
    try:
        confirm_reaction, _ = await bot.wait_for("reaction_add", check=confirm_check, timeout=120)
    except asyncio.TimeoutError:
        for m in preview_msgs:
            try:
                await m.delete()
            except Exception:
                pass
        try:
            await preview_header.delete()
        except Exception:
            pass
        await confirm_msg.edit(embed=discord.Embed(description="\u23f0 Timed out.", color=discord.Color.orange()))
        try:
            await confirm_msg.clear_reactions()
        except Exception:
            pass
        return

    for m in preview_msgs:
        try:
            await m.delete()
        except Exception:
            pass
    try:
        await preview_header.delete()
    except Exception:
        pass
    try:
        await confirm_msg.delete()
    except Exception:
        pass

    if str(confirm_reaction.emoji) == "\u274c":
        restart_msg = await ctx.send(embed=discord.Embed(
            description="\U0001f504 Starting over...",
            color=discord.Color.orange()
        ))
        await asyncio.sleep(2)
        try:
            await restart_msg.delete()
        except Exception:
            pass
        await ctx.invoke(bot.get_command("bm"))
        return

    # ── STEP 5: Send for real ──
    await do_send(target_channel, msg_type, message_content, description_text, smart_embed)
    await ctx.send(
        embed=discord.Embed(
            description=f"\u2705 Message sent to {target_channel.mention}!",
            color=discord.Color.green()
        ),
        delete_after=10
    )



# =========================
# TEST COMMANDS
# =========================
@bot.command()
@commands.is_owner()
async def testjoin(ctx):
    await on_member_join(ctx.author)
    await ctx.send("✅ Simulated join event!")

@bot.command()
@commands.is_owner()
async def testleave(ctx):
    await on_member_remove(ctx.author)
    await ctx.send("✅ Simulated leave event!")

# =========================
# SHUTDOWN
# =========================
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("🔴 Shutting down bot... See you soon!")
    await bot.close()

# =========================
# BB — INTERACTIVE MISSING CHANNEL BUILDER
# =========================

# Number emojis for up to 10 slots
BB_EMOJIS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

# Master ordered list: (channel_name, category_display_name, overwrite_type)
# overwrite_type key: "verify"|"logs"|"info"|"links"|"community"|"community_ro"|"support"|"suggestions"|"media"|"staff"
BB_CHANNEL_LIST = [
    ("verification",     "{.Σ} ───── VERIFICATION ─────", "verify"),
    ("logs",             "{.Σ} ───── LOGS ─────",         "logs"),
    ("welcome",          "{.Σ} ───── INFORMATION ─────",  "info"),
    ("rules",            "{.Σ} ───── INFORMATION ─────",  "info"),
    ("announcements",    "{.Σ} ───── INFORMATION ─────",  "info"),
    ("updates",          "{.Σ} ───── INFORMATION ─────",  "info"),
    ("roblox-group",     "{.Σ} ───── LINKS ─────",        "links"),
    ("game-links",       "{.Σ} ───── LINKS ─────",        "links"),
    ("my-profile",       "{.Σ} ───── LINKS ─────",        "links"),
    ("youtube-links",    "{.Σ} ───── LINKS ─────",        "links"),
    ("server-partnerships", "{.Σ} ───── LINKS ─────",     "links"),
    ("general",          "{.Σ} ───── COMMUNITY ─────",    "community"),
    ("memes",            "{.Σ} ───── COMMUNITY ─────",    "community"),
    ("polls",            "{.Σ} ───── COMMUNITY ─────",    "community"),
    ("questions",        "{.Σ} ───── COMMUNITY ─────",    "community"),
    ("community-codes",  "{.Σ} ───── COMMUNITY ─────",    "community"),
    ("joins",            "{.Σ} ───── COMMUNITY ─────",    "community"),
    ("leaves",           "{.Σ} ───── COMMUNITY ─────",    "community"),
    ("hall-of-shame",    "{.Σ} ───── COMMUNITY ─────",    "community_ro"),
    ("bot-commands",     "{.Σ} ───── COMMUNITY ─────",    "community_ro"),
    ("roblox-chat",      "{.Σ} ───── SUPPORT ─────",      "support"),
    ("looking-to-play",  "{.Σ} ───── SUPPORT ─────",      "support"),
    ("suggestions",      "{.Σ} ───── SUPPORT ─────",      "suggestions"),
    ("photos",           "{.Σ} ───── MEDIA ZONE ─────",   "media"),
    ("videos",           "{.Σ} ───── MEDIA ZONE ─────",   "media"),
    ("clips",            "{.Σ} ───── MEDIA ZONE ─────",   "media"),
    ("artwork",          "{.Σ} ───── MEDIA ZONE ─────",   "media"),
    ("music",            "{.Σ} ───── MEDIA ZONE ─────",   "media"),
    ("selfies",          "{.Σ} ───── MEDIA ZONE ─────",   "media"),
    ("edits",            "{.Σ} ───── MEDIA ZONE ─────",   "media"),
    ("stream-highlights","{.Σ} ───── MEDIA ZONE ─────",   "media"),
    ("staff-chat",       "{.Σ} ───── STAFF ─────",        "staff"),
    ("mod-logs",         "{.Σ} ───── STAFF ─────",        "staff"),
    ("admin-only",       "{.Σ} ───── STAFF ─────",        "staff"),
    ("private-bot-cmds", "{.Σ} ───── STAFF ─────",        "staff"),
]


async def bb_build_one(guild, ch_name, cat_name, ow_type, roles):
    """Build a single channel by name. Returns the created channel or None."""
    owner_r, admin_r, mod_r, verified_r, unverified_r, ev = roles

    def ow(read=None, send=None, history=None):
        return discord.PermissionOverwrite(
            read_messages=read, send_messages=send, read_message_history=history
        )

    def safe_ow_dict(entries):
        """Build an overwrite dict, silently skipping any None roles."""
        return {role: perms for role, perms in entries if role is not None}

    # Build overwrite dicts per type — None roles are automatically skipped
    overwrites = {
        "verify": safe_ow_dict([
            (ev,           ow(read=False, history=False)),
            (unverified_r, ow(read=True, send=True, history=True)),
            (verified_r,   ow(read=False, history=False)),
            (mod_r,        ow(read=True, send=True, history=True)),
            (admin_r,      ow(read=True, send=True, history=True)),
            (owner_r,      ow(read=True, send=True, history=True)),
        ]),
        "logs": safe_ow_dict([
            (ev,      ow(read=False, history=False)),
            (mod_r,   ow(read=True, send=True, history=True)),
            (admin_r, ow(read=True, send=True, history=True)),
            (owner_r, ow(read=True, send=True, history=True)),
        ]),
        "info": safe_ow_dict([
            (ev,         ow(read=False, send=False, history=False)),
            (verified_r, ow(read=True, send=False, history=True)),
            (mod_r,      ow(read=True, send=True, history=True)),
            (admin_r,    ow(read=True, send=True, history=True)),
            (owner_r,    ow(read=True, send=True, history=True)),
        ]),
        "links": safe_ow_dict([
            (ev,         ow(read=False, send=False, history=False)),
            (verified_r, ow(read=True, send=False, history=True)),
            (mod_r,      ow(read=True, send=True, history=True)),
            (admin_r,    ow(read=True, send=True, history=True)),
            (owner_r,    ow(read=True, send=True, history=True)),
        ]),
        "community": safe_ow_dict([
            (ev,         ow(read=False, history=False)),
            (verified_r, ow(read=True, send=True, history=True)),
            (mod_r,      ow(read=True, send=True, history=True)),
            (admin_r,    ow(read=True, send=True, history=True)),
            (owner_r,    ow(read=True, send=True, history=True)),
        ]),
        "community_ro": safe_ow_dict([
            (ev,         ow(read=False, send=False, history=False)),
            (verified_r, ow(read=True, send=False, history=True)),
            (mod_r,      ow(read=True, send=True, history=True)),
            (admin_r,    ow(read=True, send=True, history=True)),
            (owner_r,    ow(read=True, send=True, history=True)),
        ]),
        "support": safe_ow_dict([
            (ev,         ow(read=False, history=False)),
            (verified_r, ow(read=True, send=True, history=True)),
            (mod_r,      ow(read=True, send=True, history=True)),
            (admin_r,    ow(read=True, send=True, history=True)),
            (owner_r,    ow(read=True, send=True, history=True)),
        ]),
        "media": safe_ow_dict([
            (ev,         ow(read=False, history=False)),
            (verified_r, ow(read=True, send=True, history=True)),
            (mod_r,      ow(read=True, send=True, history=True)),
            (admin_r,    ow(read=True, send=True, history=True)),
            (owner_r,    ow(read=True, send=True, history=True)),
        ]),
        "staff": safe_ow_dict([
            (ev,      ow(read=False, history=False)),
            (mod_r,   ow(read=True, send=True, history=True)),
            (admin_r, ow(read=True, send=True, history=True)),
            (owner_r, ow(read=True, send=True, history=True)),
        ]),
    }

    # Get or create the category
    cat = discord.utils.get(guild.categories, name=cat_name)
    if not cat:
        cat = await guild.create_category(cat_name, overwrites=overwrites.get(ow_type, {}))

    # Special case: suggestions forum
    if ow_type == "suggestions":
        sug_ow = safe_ow_dict([
            (ev,           discord.PermissionOverwrite(read_messages=False, read_message_history=False, send_messages=False, create_public_threads=False)),
            (unverified_r, discord.PermissionOverwrite(read_messages=False, read_message_history=False, send_messages=False, create_public_threads=False)),
            (verified_r,   discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True, create_public_threads=True)),
            (mod_r,        discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True, manage_messages=True, manage_threads=True, create_public_threads=True)),
            (admin_r,      discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True, manage_messages=True, manage_threads=True, create_public_threads=True)),
            (owner_r,      discord.PermissionOverwrite(read_messages=True, read_message_history=True, send_messages=True, manage_messages=True, manage_threads=True, create_public_threads=True)),
        ])
        forum = await guild.create_forum(
            "suggestions",
            category=cat,
            topic="Got an idea? Post it here using the format guide pinned at the top!",
            overwrites=sug_ow,
            available_tags=[
                discord.ForumTag(name="💡 Idea"),
                discord.ForumTag(name="🎮 Game"),
                discord.ForumTag(name="🛡️ Server"),
                discord.ForumTag(name="🤖 Bot"),
                discord.ForumTag(name="✅ Approved"),
                discord.ForumTag(name="❌ Denied"),
                discord.ForumTag(name="👀 Under Review"),
            ]
        )
        sug_embed = discord.Embed(description=SUGGESTIONS_GUIDE, color=EMBED_COLOR)
        sug_embed.set_image(url="attachment://banner.png")
        try:
            sug_file = discord.File(BANNER_FILE, filename="banner.png")
            await forum.create_thread(
                name="📋 READ BEFORE POSTING — Suggestion Format Guide",
                embed=sug_embed,
                file=sug_file,
                auto_archive_duration=10080,
            )
        except FileNotFoundError:
            await forum.create_thread(
                name="📋 READ BEFORE POSTING — Suggestion Format Guide",
                embed=sug_embed,
                auto_archive_duration=10080,
            )
        return forum

    # Normal text channel
    ch_ow = overwrites.get(ow_type, {})
    ch = await guild.create_text_channel(ch_name, category=cat, overwrites=ch_ow)
    await send_channel_embed(ch, ch_name)
    return ch


def bb_build_embed(missing_page, built_names, total_missing_count):
    """Build the status embed for the !bb interactive session."""
    lines = []
    for i, (ch_name, _, _) in enumerate(missing_page):
        emoji = BB_EMOJIS[i]
        if ch_name in built_names:
            lines.append(f"{emoji} ~~`{ch_name}`~~ ✅")
        else:
            lines.append(f"{emoji} `{ch_name}`")

    remaining = len([e for e in missing_page if e[0] not in built_names])
    description = (
        f"Found **{total_missing_count}** missing channel(s). Showing up to 10.\n\n"
        + "\n".join(lines)
        + f"\n\n{'━'*30}\n"
        + f"React with the number to build that channel.\n"
        + f"Type **`All`** in chat to build everything at once.\n"
        + f"Session times out after **120s** of inactivity."
    )
    embed = discord.Embed(
        title="🔍 Missing Channels",
        description=description,
        color=EMBED_COLOR
    )
    embed.set_footer(text=f"{remaining} remaining on this page")
    return embed


@bot.command()
@commands.is_owner()
async def bb(ctx):
    """Interactively build missing channels one at a time or all at once."""
    guild = ctx.guild
    scanning_msg = await ctx.send("🔍 Scanning for missing channels...")

    # Fetch roles — any that don't exist are None and safely skipped in overwrites
    owner_r      = discord.utils.get(guild.roles, name="{.Σ} Owner")
    admin_r      = discord.utils.get(guild.roles, name="{.Σ} Admin")
    mod_r        = discord.utils.get(guild.roles, name="{.Σ} Moderator")
    verified_r   = discord.utils.get(guild.roles, name="✅ Verified")
    unverified_r = discord.utils.get(guild.roles, name="❌ Unverified")
    ev           = guild.default_role
    roles        = (owner_r, admin_r, mod_r, verified_r, unverified_r, ev)

    missing_roles = [n for n, r in [
        ("{.Σ} Owner", owner_r), ("{.Σ} Admin", admin_r), ("{.Σ} Moderator", mod_r),
        ("✅ Verified", verified_r), ("❌ Unverified", unverified_r)
    ] if r is None]
    if missing_roles:
        await scanning_msg.edit(
            content=(
                f"⚠️ Some roles are missing: {', '.join(f'`{r}`' for r in missing_roles)}\n"
                f"Channels will still be built but **without permissions** for those roles. "
                f"Run `!fixperms all` after creating the roles to apply them.\n\n"
                f"Continuing scan in 3 seconds..."
            )
        )
        await asyncio.sleep(3)

    # Find missing channels (up to 10 shown at a time)
    existing = {ch.name for ch in guild.channels}
    all_missing = [(ch, cat, owt) for (ch, cat, owt) in BB_CHANNEL_LIST if ch not in existing]

    if not all_missing:
        await scanning_msg.edit(content="✅ All channels already exist — nothing to build!")
        return

    page = all_missing[:10]
    total_missing = len(all_missing)
    built_names = set()

    # Send the interactive embed
    embed = bb_build_embed(page, built_names, total_missing)
    await scanning_msg.delete()
    panel = await ctx.send(embed=embed)

    # Add number reactions for each slot on this page
    for i in range(len(page)):
        await panel.add_reaction(BB_EMOJIS[i])

    # ── Event listeners ──
    def reaction_check(reaction, user):
        return (
            user == ctx.author
            and reaction.message.id == panel.id
            and str(reaction.emoji) in BB_EMOJIS[:len(page)]
        )

    def message_check(m):
        return (
            m.author == ctx.author
            and m.channel == ctx.channel
            and m.content.strip().lower() == "all"
        )

    # ── Interactive loop ──
    while True:
        # Check if everything on this page is already built
        remaining_on_page = [e for e in page if e[0] not in built_names]
        if not remaining_on_page:
            await panel.edit(embed=discord.Embed(
                title="✅ All Done!",
                description=f"Built **{len(built_names)}** channel(s) successfully!\n" +
                            "\n".join(f"✅ `{n}`" for n in built_names),
                color=discord.Color.green()
            ))
            try:
                await panel.clear_reactions()
            except:
                pass
            break

        try:
            done, _ = await asyncio.wait(
                [
                    asyncio.ensure_future(bot.wait_for("reaction_add", check=reaction_check, timeout=120)),
                    asyncio.ensure_future(bot.wait_for("message",      check=message_check,  timeout=120)),
                ],
                return_when=asyncio.FIRST_COMPLETED
            )
        except asyncio.TimeoutError:
            await panel.edit(embed=discord.Embed(
                title="⏰ Session Timed Out",
                description=f"Built **{len(built_names)}** channel(s) before timing out.\n" +
                            (("\n".join(f"✅ `{n}`" for n in built_names)) if built_names else "_None built._"),
                color=discord.Color.orange()
            ))
            try:
                await panel.clear_reactions()
            except:
                pass
            break

        # Cancel the other pending future
        for future in done:
            pass
        # Collect result from whichever fired
        result = None
        timed_out = False
        for future in done:
            try:
                result = future.result()
            except asyncio.TimeoutError:
                timed_out = True

        if timed_out:
            await panel.edit(embed=discord.Embed(
                title="⏰ Session Timed Out",
                description=f"Built **{len(built_names)}** channel(s) before timing out.\n" +
                            (("\n".join(f"✅ `{n}`" for n in built_names)) if built_names else "_None built._"),
                color=discord.Color.orange()
            ))
            try:
                await panel.clear_reactions()
            except:
                pass
            break

        # ── "All" typed in chat ──
        if isinstance(result, discord.Message):
            try:
                await result.delete()
            except:
                pass
            building_embed = discord.Embed(
                title="⚙️ Building All Missing Channels...",
                description="Please wait, this may take a moment.",
                color=EMBED_COLOR
            )
            await panel.edit(embed=building_embed)
            try:
                await panel.clear_reactions()
            except:
                pass

            for (ch_name, cat_name, ow_type) in page:
                if ch_name not in built_names:
                    try:
                        await bb_build_one(guild, ch_name, cat_name, ow_type, roles)
                        built_names.add(ch_name)
                    except Exception as e:
                        print(f"[BB] Error building {ch_name}: {e}")

            await panel.edit(embed=discord.Embed(
                title="✅ All Done!",
                description=f"Built **{len(built_names)}** channel(s) successfully!\n" +
                            "\n".join(f"✅ `{n}`" for n in built_names),
                color=discord.Color.green()
            ))
            break

        # ── Reaction picked ──
        if isinstance(result, tuple):
            reaction, user = result
            # Remove their reaction so they can react again if needed
            try:
                await panel.remove_reaction(reaction.emoji, user)
            except:
                pass

            idx = BB_EMOJIS.index(str(reaction.emoji))
            if idx >= len(page):
                continue

            ch_name, cat_name, ow_type = page[idx]

            if ch_name in built_names:
                continue  # already built, ignore

            # Update embed to show "building..."
            building_lines = []
            for i, (cn, _, _) in enumerate(page):
                e = BB_EMOJIS[i]
                if cn in built_names:
                    building_lines.append(f"{e} ~~`{cn}`~~ ✅")
                elif cn == ch_name:
                    building_lines.append(f"{e} `{cn}` ⚙️ *building...*")
                else:
                    building_lines.append(f"{e} `{cn}`")
            building_embed = discord.Embed(
                title="🔍 Missing Channels",
                description=(
                    f"Found **{total_missing}** missing channel(s). Showing up to 10.\n\n"
                    + "\n".join(building_lines)
                    + f"\n\n{'━'*30}\n"
                    + f"React with the number to build that channel.\n"
                    + f"Type **`All`** in chat to build everything at once."
                ),
                color=EMBED_COLOR
            )
            await panel.edit(embed=building_embed)

            try:
                await bb_build_one(guild, ch_name, cat_name, ow_type, roles)
                built_names.add(ch_name)
            except Exception as e:
                await ctx.send(f"❌ Failed to build `{ch_name}`: {e}", delete_after=10)

            # Refresh the panel embed
            await panel.edit(embed=bb_build_embed(page, built_names, total_missing))

# =========================
# START
# =========================
keep_alive()
bot.run(TOKEN)
