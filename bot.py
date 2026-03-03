import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import asyncio

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
    "general":           "💬 The main hangout spot. Talk about anything and everything here!",
    "memes":             "😂 Post the funniest memes you find. Keep it appropriate!",
    "polls":             "📊 Community polls are posted here. Vote and make your voice heard!",
    "questions":         "❓ Have a question about the server, game, or community? Ask here!",
    "hall-of-shame":     "😬 Post your most embarrassing moments, worst fails, and biggest L's here. Keep it fun, not personal attacks!",
    "bot-commands":      "🤖 Use all bot commands in this channel to keep other channels clean.",
    "community-codes":   "🎁 Community codes and giveaways are dropped here. Stay active to catch them!",
    "roblox-chat":       "🎮 Talk about Roblox games, updates, and anything Roblox related here!",
    "game-suggestions":  "💡 Got an idea for a game or feature? Drop your suggestions here!",
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
    "joins":             "📥 Member join logs are recorded here automatically.",
    "leaves":            "📤 Member leave logs are recorded here automatically.",
    "private-bot-cmds":  "🤖 Private channel for owner bot commands only.",
}

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
# HELPER: SEND BANNER
# =========================
async def send_banner(channel):
    await channel.send(file=discord.File(BANNER_FILE))

# =========================
# HELPER: SEND CHANNEL EMBED
# Banner first, then embed below it. Used for build and updatechan.
# =========================
async def send_channel_embed(channel, channel_key=None):
    if channel_key is None:
        channel_key = channel.name.replace("{.Σ}-", "").replace("{.σ}-", "")
    description = CHANNEL_EMBEDS.get(channel_key, f"Welcome to {channel.name}. Keep it clean and follow the rules.")
    await send_banner(channel)
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

    # WELCOME CHANNEL - no banner, just the player join embed
    welcome_channel = discord.utils.get(guild.text_channels, name="{.Σ}-welcome")
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
    joins_channel = discord.utils.get(guild.text_channels, name="{.Σ}-joins")
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
    logs = discord.utils.get(guild.text_channels, name="{.Σ}-logs")
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
    leaves_channel = discord.utils.get(guild.text_channels, name="{.Σ}-leaves")
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
    logs = discord.utils.get(guild.text_channels, name="{.Σ}-logs")
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
    logs = discord.utils.get(message.guild.text_channels, name="{.Σ}-logs")
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
    ch = await guild.create_text_channel("{.Σ}-verification", category=verify_cat, overwrites=verify_ow)
    await send_channel_embed(ch, "verification")

    logs_ow = {
        ev:      ow(read=False, history=False),
        mod_r:   ow(read=True, send=True, history=True),
        admin_r: ow(read=True, send=True, history=True),
        owner_r: ow(read=True, send=True, history=True),
    }
    logs_cat = await guild.create_category("{.Σ} ───── LOGS ─────", overwrites=logs_ow)
    await guild.create_text_channel("{.Σ}-logs", category=logs_cat, overwrites=logs_ow)

    # INFORMATION
    info_ow = {
        ev:        ow(read=False, send=False, history=False),
        verified_r: ow(read=True, send=False, history=True),
        mod_r:     ow(read=True, send=True, history=True),
        admin_r:   ow(read=True, send=True, history=True),
        owner_r:   ow(read=True, send=True, history=True),
    }
    info_cat = await guild.create_category("{.Σ} ───── INFORMATION ─────", overwrites=info_ow)
    for ch_name in ["welcome", "rules", "announcements", "updates"]:
        ch = await guild.create_text_channel(f"{{.Σ}}-{ch_name}", category=info_cat, overwrites=info_ow)
        await send_channel_embed(ch, ch_name)

    # LINKS
    links_ow = {
        ev:        ow(read=False, send=False, history=False),
        verified_r: ow(read=True, send=False, history=True),
        mod_r:     ow(read=True, send=True, history=True),
        admin_r:   ow(read=True, send=True, history=True),
        owner_r:   ow(read=True, send=True, history=True),
    }
    links_cat = await guild.create_category("{.Σ} ───── LINKS ─────", overwrites=links_ow)
    for ch_name in ["roblox-group", "game-links", "my-profile", "youtube-links"]:
        ch = await guild.create_text_channel(f"{{.Σ}}-{ch_name}", category=links_cat, overwrites=links_ow)
        await send_channel_embed(ch, ch_name)

    # COMMUNITY
    community_ow = {
        ev:        ow(read=False, history=False),
        verified_r: ow(read=True, send=True, history=True),
        mod_r:     ow(read=True, send=True, history=True),
        admin_r:   ow(read=True, send=True, history=True),
        owner_r:   ow(read=True, send=True, history=True),
    }
    community_readonly_ow = {
        ev:        ow(read=False, send=False, history=False),
        verified_r: ow(read=True, send=False, history=True),
        mod_r:     ow(read=True, send=True, history=True),
        admin_r:   ow(read=True, send=True, history=True),
        owner_r:   ow(read=True, send=True, history=True),
    }
    community_cat = await guild.create_category("{.Σ} ───── COMMUNITY ─────", overwrites=community_ow)
    for ch_name in ["general", "memes", "polls", "questions", "community-codes"]:
        ch = await guild.create_text_channel(f"{{.Σ}}-{ch_name}", category=community_cat, overwrites=community_ow)
        await send_channel_embed(ch, ch_name)
    for ch_name in ["hall-of-shame", "bot-commands"]:
        ch = await guild.create_text_channel(f"{{.Σ}}-{ch_name}", category=community_cat, overwrites=community_readonly_ow)
        await send_channel_embed(ch, ch_name)

    # GAMING
    gaming_ow = {
        ev:        ow(read=False, history=False),
        verified_r: ow(read=True, send=True, history=True),
        mod_r:     ow(read=True, send=True, history=True),
        admin_r:   ow(read=True, send=True, history=True),
        owner_r:   ow(read=True, send=True, history=True),
    }
    gaming_cat = await guild.create_category("{.Σ} ───── GAMING ─────", overwrites=gaming_ow)
    for ch_name in ["roblox-chat", "game-suggestions", "looking-to-play"]:
        ch = await guild.create_text_channel(f"{{.Σ}}-{ch_name}", category=gaming_cat, overwrites=gaming_ow)
        await send_channel_embed(ch, ch_name)

    # MEDIA ZONE
    media_ow = {
        ev:        ow(read=False, history=False),
        verified_r: ow(read=True, send=True, history=True),
        mod_r:     ow(read=True, send=True, history=True),
        admin_r:   ow(read=True, send=True, history=True),
        owner_r:   ow(read=True, send=True, history=True),
    }
    media_cat = await guild.create_category("{.Σ} ───── MEDIA ZONE ─────", overwrites=media_ow)
    for ch_name in ["photos", "videos", "clips", "artwork", "music", "selfies", "edits", "stream-highlights"]:
        ch = await guild.create_text_channel(f"{{.Σ}}-{ch_name}", category=media_cat, overwrites=media_ow)
        await send_channel_embed(ch, ch_name)

    # STAFF
    staff_ow = {
        ev:      ow(read=False, history=False),
        mod_r:   ow(read=True, send=True, history=True),
        admin_r: ow(read=True, send=True, history=True),
        owner_r: ow(read=True, send=True, history=True),
    }
    staff_visible_ow = {
        ev:        ow(read=False, history=False),
        verified_r: ow(read=True, send=False, history=True),
        mod_r:     ow(read=True, send=True, history=True),
        admin_r:   ow(read=True, send=True, history=True),
        owner_r:   ow(read=True, send=True, history=True),
    }
    staff_cat = await guild.create_category("{.Σ} ───── STAFF ─────", overwrites=staff_ow)
    for ch_name in ["staff-chat", "mod-logs", "admin-only", "private-bot-cmds"]:
        ch = await guild.create_text_channel(f"{{.Σ}}-{ch_name}", category=staff_cat, overwrites=staff_ow)
        await send_channel_embed(ch, ch_name)
    for ch_name in ["joins", "leaves"]:
        ch = await guild.create_text_channel(f"{{.Σ}}-{ch_name}", category=staff_cat, overwrites=staff_visible_ow)
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
        ch_key = channel.name.replace("{.Σ}-", "").replace("{.σ}-", "")
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
            if "welcome" in ch.name or "verification" in ch.name:
                await ch.set_permissions(unverified_r, read_messages=True, read_message_history=True)
            await msg.edit(content=f"✅ Fixed permissions for {ch.mention}")
        except Exception as e:
            await msg.edit(content=f"❌ Error: {str(e)}")
        return

    target = target.lower()
    cats_to_fix = ["links", "information", "community", "verification", "gaming", "media"] if target == "all" else [target]

    for cat in ctx.guild.categories:
        if any(c in cat.name.lower() for c in cats_to_fix):
            for ch in cat.channels:
                try:
                    await ch.set_permissions(ctx.guild.default_role, read_messages=True, read_message_history=True)
                    await ch.set_permissions(unverified_r, read_messages=False, read_message_history=False)
                    if "welcome" in ch.name or "verification" in ch.name:
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
            ch_type = "💬" if isinstance(ch, discord.TextChannel) else "🔊"
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

    private_ch = discord.utils.get(guild.text_channels, name="{.Σ}-private-bot-cmds")
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
# START
# =========================
keep_alive()
bot.run(TOKEN)
