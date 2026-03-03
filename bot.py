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
bot = commands.Bot(command_prefix="!", intents=intents)

DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
BANNER_FILE = "banner.png"

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
# SEND BANNER FUNCTION
# =========================
async def send_banner(channel):
    if os.path.exists(BANNER_FILE):
        await channel.send(file=discord.File(BANNER_FILE))

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is online.")

# =========================
# MEMBER JOIN
# =========================
@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="{.Σ}-welcome")
    if welcome_channel:
        await send_banner(welcome_channel)
        embed = discord.Embed(
            title=f"👋 Welcome {member.name}!",
            description=f"Hey {member.mention}! Welcome to **{member.guild.name}**!\n\n📖 **Please read the rules** and head to verification to get started!",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="📋 Next Steps",
            value="1️⃣ Read the rules\n2️⃣ Get verified\n3️⃣ Enjoy the server!",
            inline=False
        )
        embed.set_footer(text=f"Member #{member.guild.member_count}", icon_url=member.guild.icon.url if member.guild.icon else None)
        embed.timestamp = discord.utils.utcnow()
        await welcome_channel.send(embed=embed)
        await welcome_channel.send(DIVIDER)

    logs = discord.utils.get(member.guild.channels, name="{.Σ}-logs")
    if logs:
        embed = discord.Embed(
            title="✅ Member Joined",
            description=f"{member.mention} joined the server.",
            color=discord.Color.green()
        )
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Member Count", value=str(member.guild.member_count), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await logs.send(embed=embed)

# =========================
# MEMBER LEAVE
# =========================
@bot.event
async def on_member_remove(member):
    logs = discord.utils.get(member.guild.channels, name="{.Σ}-logs")
    if logs:
        embed = discord.Embed(
            title="❌ Member Left",
            description=f"**{member.name}** left the server.",
            color=discord.Color.red()
        )
        if member.joined_at:
            embed.add_field(name="Time with us", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Members Remaining", value=str(member.guild.member_count), inline=True)
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
    logs = discord.utils.get(message.guild.channels, name="{.Σ}-logs")
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
    await ctx.send("⚙️ Building full pro setup...")

    roles = {
        "{.Σ} Owner": discord.Color.red(),
        "{.Σ} Admin": discord.Color.dark_red(),
        "{.Σ} Moderator": discord.Color.orange(),
        "{.Σ} Media Team": discord.Color.purple(),
        "{.Σ} VIP": discord.Color.gold(),
        "✅ Verified": discord.Color.green(),
        "❌ Unverified": discord.Color.dark_gray(),
        "🎮 Gamer": discord.Color.blue(),
        "🎵 Music Addict": discord.Color.magenta(),
        "😂 Meme Lord": discord.Color.teal(),
        "🔥 Active": discord.Color.brand_red(),
        "Muted": discord.Color.dark_grey(),
    }

    created_roles = {}
    for name, color in roles.items():
        role = await guild.create_role(name=name, color=color)
        created_roles[name] = role

    verify_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        created_roles["❌ Unverified"]: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    verify_category = await guild.create_category("{.Σ} ───── VERIFICATION ─────", overwrites=verify_overwrites)
    verification_channel = await guild.create_text_channel("{.Σ}-verification", category=verify_category)

    logs_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        created_roles["{.Σ} Admin"]: discord.PermissionOverwrite(read_messages=True),
        created_roles["{.Σ} Moderator"]: discord.PermissionOverwrite(read_messages=True)
    }
    logs_category = await guild.create_category("{.Σ} ───── LOGS ─────", overwrites=logs_overwrites)
    logs_channel = await guild.create_text_channel("{.Σ}-logs", category=logs_category)

    structure = {
        "{.Σ} ───── INFORMATION ─────": ["welcome", "rules", "announcements"],
        "{.Σ} ───── COMMUNITY ─────": ["general", "chat", "memes", "polls", "questions"],
        "{.Σ} ───── LINKS ─────": ["youtube", "twitch", "socials", "partnerships"],
        "{.Σ} ───── MEDIA ZONE ─────": ["photos", "videos", "clips", "artwork", "music", "selfies", "gaming-clips", "edits", "stream-highlights"],
        "{.Σ} ───── STAFF ─────": ["staff-chat", "mod-logs", "admin-only"]
    }

    for category_name, channels in structure.items():
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True),
            created_roles["❌ Unverified"]: discord.PermissionOverwrite(read_messages=False)
        }
        if "STAFF" in category_name:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                created_roles["{.Σ} Admin"]: discord.PermissionOverwrite(read_messages=True),
                created_roles["{.Σ} Moderator"]: discord.PermissionOverwrite(read_messages=True)
            }
        if "INFORMATION" in category_name:
            overwrites[created_roles["❌ Unverified"]] = discord.PermissionOverwrite(read_messages=True, send_messages=False)

        category = await guild.create_category(category_name, overwrites=overwrites)
        for channel_name in channels:
            channel = await guild.create_text_channel(f"{{.Σ}}-{channel_name}", category=category)
            embed = discord.Embed(
                title=f"Welcome to {{.Σ}} {channel_name}",
                description="Keep it clean and follow the rules.",
                color=discord.Color.purple()
            )
            await channel.send(embed=embed)

    await ctx.send("✅ Full pro server setup complete.")

# =========================
# WIPE SERVER COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def wipe(ctx):
    await ctx.send("⚠️ Type CONFIRM to wipe the server.")

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
    """Clear and rebuild a specific channel"""
    msg = await ctx.send(f"🔄 Clearing and rebuilding {channel.mention}...")
    try:
        deleted = await channel.purge(limit=None)
        if channel.category:
            await channel.edit(sync_permissions=True)
        channel_name = channel.name.replace("{.Σ}-", "")
        embed = discord.Embed(
            title=f"Welcome to {{.Σ}} {channel_name}",
            description="Keep it clean and follow the rules.",
            color=discord.Color.purple()
        )
        await channel.send(embed=embed)
        await msg.edit(content=f"✅ Successfully rebuilt {channel.mention}! Deleted {len(deleted)} messages.")
    except Exception as e:
        await msg.edit(content=f"❌ Error: {str(e)}")

# =========================
# FIX PERMISSIONS COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def fixperms(ctx, *, target=None):
    """Fix permissions for channels/categories"""
    if not target:
        await ctx.send("❌ Usage: `!fixperms #channel`, `!fixperms category_name`, or `!fixperms all`")
        return

    unverified_role = discord.utils.get(ctx.guild.roles, name="❌ Unverified")
    if not unverified_role:
        await ctx.send("❌ Could not find '❌ Unverified' role!")
        return

    msg = await ctx.send("🔄 Fixing permissions...")
    fixed_count = 0

    if ctx.message.channel_mentions:
        channel = ctx.message.channel_mentions[0]
        try:
            await channel.set_permissions(ctx.guild.default_role, read_messages=True, read_message_history=True)
            await channel.set_permissions(unverified_role, read_messages=False, read_message_history=False)
            if "welcome" in channel.name or "verification" in channel.name:
                await channel.set_permissions(unverified_role, read_messages=True, read_message_history=True)
            await msg.edit(content=f"✅ Fixed permissions for {channel.mention}")
        except Exception as e:
            await msg.edit(content=f"❌ Error: {str(e)}")
        return

    target = target.lower()
    categories_to_fix = ["links", "information", "community", "verification"] if target == "all" else [target]

    for category in ctx.guild.categories:
        if any(cat in category.name.lower() for cat in categories_to_fix):
            for channel in category.channels:
                try:
                    await channel.set_permissions(ctx.guild.default_role, read_messages=True, read_message_history=True)
                    await channel.set_permissions(unverified_role, read_messages=False, read_message_history=False)
                    if "welcome" in channel.name or "verification" in channel.name:
                        await channel.set_permissions(unverified_role, read_messages=True, read_message_history=True)
                    fixed_count += 1
                except Exception as e:
                    print(f"Error fixing {channel.name}: {e}")

    await msg.edit(content=f"✅ Fixed permissions for {fixed_count} channels!")

# =========================
# SCAN COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def scan(ctx):
    """Scan entire server and output all details to a file"""
    await ctx.send("🔍 Scanning server... This might take a minute.")
    guild = ctx.guild
    output = []

    output.append("="*50)
    output.append(f"SERVER SCAN: {guild.name}")
    output.append(f"Server ID: {guild.id}")
    output.append(f"Owner: {guild.owner}")
    output.append(f"Member Count: {guild.member_count}")
    output.append("="*50)
    output.append("")

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
    for category in guild.categories:
        output.append(f"\n📂 CATEGORY: {category.name}")
        output.append(f"   ID: {category.id}")
        output.append(f"   Position: {category.position}")
        output.append(f"   PERMISSIONS:")
        for target, overwrite in category.overwrites.items():
            output.append(f"      {target.name}:")
            perms = [f"{perm}: {value}" for perm, value in overwrite if value is not None]
            output.append(f"         {', '.join(perms)}")
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):
                output.append(f"\n   💬 TEXT CHANNEL: {channel.name}")
            elif isinstance(channel, discord.VoiceChannel):
                output.append(f"\n   🔊 VOICE CHANNEL: {channel.name}")
            output.append(f"      ID: {channel.id}")
            output.append(f"      Position: {channel.position}")
            if isinstance(channel, discord.TextChannel):
                output.append(f"      Topic: {channel.topic}")
                output.append(f"      NSFW: {channel.nsfw}")
                output.append(f"      Slowmode: {channel.slowmode_delay}s")
            output.append(f"      PERMISSIONS:")
            for target, overwrite in channel.overwrites.items():
                output.append(f"         {target.name}:")
                perms = [f"{perm}: {value}" for perm, value in overwrite if value is not None]
                if perms:
                    output.append(f"            {', '.join(perms)}")
            if isinstance(channel, discord.TextChannel):
                try:
                    messages = [msg async for msg in channel.history(limit=5)]
                    if messages:
                        output.append(f"      RECENT MESSAGES (last 5):")
                        for msg in reversed(messages):
                            content = msg.content[:100] if msg.content else "[No text content]"
                            output.append(f"         [{msg.author.name}]: {content}")
                            if msg.embeds:
                                output.append(f"            [Has {len(msg.embeds)} embed(s)]")
                                for embed in msg.embeds:
                                    output.append(f"               Title: {embed.title}")
                                    output.append(f"               Description: {embed.description[:100] if embed.description else 'None'}")
                                    output.append(f"               Color: {embed.color}")
                                    if embed.fields:
                                        for field in embed.fields:
                                            output.append(f"               Field: {field.name} = {field.value[:50]}")
                except:
                    output.append(f"      [Could not read messages]")

    output.append(f"\n📂 CHANNELS (No Category):")
    for channel in guild.channels:
        if channel.category is None:
            if isinstance(channel, discord.TextChannel):
                output.append(f"\n   💬 TEXT CHANNEL: {channel.name}")
            elif isinstance(channel, discord.VoiceChannel):
                output.append(f"\n   🔊 VOICE CHANNEL: {channel.name}")
            output.append(f"      ID: {channel.id}")
            output.append(f"      PERMISSIONS:")
            for target, overwrite in channel.overwrites.items():
                output.append(f"         {target.name}:")
                perms = [f"{perm}: {value}" for perm, value in overwrite if value is not None]
                if perms:
                    output.append(f"            {', '.join(perms)}")

    output.append("\n" + "="*50 + "\n")
    output.append("👥 MEMBERS:")
    output.append("-"*50)
    for member in guild.members:
        output.append(f"\nMember: {member.name} ({member.display_name})")
        output.append(f"  ID: {member.id}")
        output.append(f"  Bot: {member.bot}")
        output.append(f"  Joined: {member.joined_at}")
        output.append(f"  Roles: {', '.join([r.name for r in member.roles[1:]])}")
        output.append(f"  Top Role: {member.top_role.name}")
        output.append(f"  Permissions (server-wide): {member.guild_permissions.value}")

    output.append("\n" + "="*50 + "\n")
    output.append("😀 EMOJIS:")
    output.append("-"*50)
    for emoji in guild.emojis:
        output.append(f"  {emoji.name} - ID: {emoji.id} - Animated: {emoji.animated}")
    output.append("\n" + "="*50)

    filename = f"/tmp/server_scan_{guild.id}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    private_channel = discord.utils.get(guild.text_channels, name="private-bot-cmds")
    if private_channel:
        await private_channel.send(f"✅ Server scan complete! Total lines: {len(output)}", file=discord.File(filename))
        await ctx.send(f"✅ Scan complete! Results sent to {private_channel.mention}")
    else:
        await ctx.send(f"⚠️ Could not find #private-bot-cmds channel. Sending here instead.", file=discord.File(filename))

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
    """Clear messages in current channel"""
    if amount > 100:
        await ctx.send("❌ Cannot delete more than 100 messages at once!")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ Deleted {len(deleted)-1} messages!")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    """Kick a member"""
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
    """Ban a member"""
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
    """Unban a user by ID"""
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ Unbanned **{user.name}**")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    """Add a role to a member"""
    await member.add_roles(role)
    await ctx.send(f"✅ Added {role.mention} to {member.mention}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    """Remove a role from a member"""
    await member.remove_roles(role)
    await ctx.send(f"✅ Removed {role.mention} from {member.mention}")

# =========================
# INFO COMMANDS
# =========================
@bot.command()
async def serverinfo(ctx):
    """Display server information"""
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blue())
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
    """Display user information"""
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🏷️ Display Name", value=member.display_name, inline=True)
    embed.add_field(name="🆔 User ID", value=member.id, inline=True)
    embed.add_field(name="📅 Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=False)
    if member.joined_at:
        embed.add_field(name="📥 Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=False)
    roles = [role.mention for role in member.roles[1:]]
    if roles:
        embed.add_field(name=f"🎭 Roles [{len(roles)}]", value=" ".join(roles[:10]), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: **{latency}ms**")

# =========================
# BOTCOMMANDS (was 'commands' - renamed to fix AttributeError crash)
# =========================
@bot.command()
async def botcommands(ctx):
    """Display all commands"""
    embed = discord.Embed(
        title="🤖 {.Σ} Bot Commands",
        description="Here are all available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="👑 Owner Only",
        value="`!build` - Build server structure\n`!wipe` - Wipe server\n`!updatechan #channel` - Rebuild channel\n`!fixperms <target>` - Fix permissions\n`!scan` - Scan server details\n`!shutdown` - Shut down bot",
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
    """Simulate a member joining"""
    await on_member_join(ctx.author)
    await ctx.send("✅ Simulated join event!")

@bot.command()
@commands.is_owner()
async def testleave(ctx):
    """Simulate a member leaving"""
    await on_member_remove(ctx.author)
    await ctx.send("✅ Simulated leave event!")

# =========================
# SHUTDOWN COMMAND
# =========================
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    """Shut down the bot"""
    await ctx.send("🔴 Shutting down bot... See you soon!")
    await bot.close()

# =========================
# START EVERYTHING
# =========================
keep_alive()
bot.run(TOKEN)
