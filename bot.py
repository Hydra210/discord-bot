import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# =========================
# TOKEN FROM RENDER ENV
# =========================
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# KEEP ALIVE WEB SERVER
# =========================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# =========================
# BUILD SERVER COMMAND
# =========================
@bot.command()
@commands.has_permissions(administrator=True)
async def build(ctx):

    guild = ctx.guild
    await ctx.send("⚙️ Building full pro setup...")

    # ===== ROLES =====
    roles = {
        "{.Σ} Owner": discord.Color.red(),
        "{.Σ} Admin": discord.Color.dark_red(),
        "{.Σ} Moderator": discord.Color.orange(),
        "{.Σ} Media Team": discord.Color.purple(),
        "{.Σ} VIP": discord.Color.gold(),
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

    # ===== VERIFICATION + LOGS CATEGORY =====
    verify_category = await guild.create_category("{.Σ} ───── VERIFICATION ─────")

    await guild.create_text_channel("{.Σ}-verification", category=verify_category)
    logs_channel = await guild.create_text_channel("{.Σ}-logs", category=verify_category)

    # ===== MAIN STRUCTURE =====
    structure = {
        "{.Σ} ───── INFORMATION ─────": [
            "welcome",
            "rules",
            "announcements"
        ],
        "{.Σ} ───── COMMUNITY ─────": [
            "general",
            "chat",
            "memes",
            "polls",
            "questions"
        ],
        "{.Σ} ───── MEDIA ZONE ─────": [
            "photos",
            "videos",
            "clips",
            "artwork",
            "music",
            "selfies",
            "gaming-clips",
            "edits",
            "stream-highlights",
            "youtube-links"
        ],
        "{.Σ} ───── STAFF ─────": [
            "staff-chat",
            "mod-logs",
            "admin-only"
        ]
    }

    for category_name, channels in structure.items():

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True)
        }

        if "STAFF" in category_name:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                created_roles["{.Σ} Admin"]: discord.PermissionOverwrite(read_messages=True),
                created_roles["{.Σ} Moderator"]: discord.PermissionOverwrite(read_messages=True)
            }

        category = await guild.create_category(category_name, overwrites=overwrites)

        for channel_name in channels:
            channel = await guild.create_text_channel(
                f"{{.Σ}}-{channel_name}",
                category=category
            )

            embed = discord.Embed(
                title=f"Welcome to {{.Σ}} {channel_name}",
                description="Keep it clean and follow the rules.",
                color=discord.Color.random()
            )

            await channel.send(embed=embed)

    await ctx.send("✅ Full pro server setup complete.")

# =========================
# WIPE SERVER COMMAND
# =========================
@bot.command()
@commands.has_permissions(administrator=True)
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
# MEMBER JOIN LOG
# =========================
@bot.event
async def on_member_join(member):

    logs = discord.utils.get(member.guild.channels, name="{.Σ}-logs")
    if logs:
        embed = discord.Embed(
            title="Member Joined",
            description=f"{member.mention} joined the server.",
            color=discord.Color.green()
        )
        await logs.send(embed=embed)

# =========================
# MEMBER LEAVE LOG
# =========================
@bot.event
async def on_member_remove(member):

    logs = discord.utils.get(member.guild.channels, name="{.Σ}-logs")
    if logs:
        embed = discord.Embed(
            title="Member Left",
            description=f"{member.name} left the server.",
            color=discord.Color.red()
        )
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
            title="Message Deleted",
            description=f"User: {message.author}\nChannel: {message.channel.mention}\nContent: {message.content}",
            color=discord.Color.orange()
        )
        await logs.send(embed=embed)

# =========================
# START EVERYTHING
# =========================
keep_alive()
bot.run(TOKEN)