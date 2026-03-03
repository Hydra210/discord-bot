import discord
from discord.ext import commands
import os
from threading import Thread
from flask import Flask

# ===============================
# FLASK WEB SERVER
# ===============================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

def run_web():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

# ===============================
# INTENTS
# ===============================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Required for prefix commands
bot = commands.Bot(command_prefix="!", intents=intents)

DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
BANNER_FILE = "banner.png"  # Put banner.png in same folder

# ===============================
# READY EVENT
# ===============================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is online.")

# ===============================
# SEND BANNER FUNCTION
# ===============================
async def send_banner(channel):
    if os.path.exists(BANNER_FILE):
        await channel.send(file=discord.File(BANNER_FILE))
    else:
        await channel.send("Banner file not found.")

# ===============================
# MEMBER JOIN
# ===============================
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="joins")
    if not channel:
        return
    # 1 Banner
    await send_banner(channel)
    # 2 Embed
    embed = discord.Embed(
        title=f"Welcome {member.mention} to {member.guild.name}",
        color=discord.Color.dark_grey()
    )
    embed.set_author(
        name="Member Joined",
        icon_url=member.display_avatar.url
    )
    embed.add_field(
        name="Account Created",
        value=f"<t:{int(member.created_at.timestamp())}:R>",
        inline=False
    )
    embed.add_field(
        name="Member Count",
        value=str(member.guild.member_count),
        inline=False
    )
    embed.add_field(
        name="User ID",
        value=str(member.id),
        inline=False
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.name} • New Arrival")
    embed.timestamp = discord.utils.utcnow()
    await channel.send(embed=embed)
    # 3 Divider
    await channel.send(DIVIDER)

# ===============================
# MEMBER LEAVE
# ===============================
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="leaves")
    if not channel:
        return
    # 1 Banner
    await send_banner(channel)
    # 2 Embed
    embed = discord.Embed(
        title=f"{member.name} has left {member.guild.name}",
        color=discord.Color.dark_gray()
    )
    embed.set_author(
        name="Member Left",
        icon_url=member.display_avatar.url
    )
    if member.joined_at:
        embed.add_field(
            name="Joined Server",
            value=f"<t:{int(member.joined_at.timestamp())}:R>",
            inline=False
        )
    embed.add_field(
        name="Members Remaining",
        value=str(member.guild.member_count),
        inline=False
    )
    embed.add_field(
        name="User ID",
        value=str(member.id),
        inline=False
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.name} • Departure Logged")
    embed.timestamp = discord.utils.utcnow()
    await channel.send(embed=embed)
    # 3 Divider
    await channel.send(DIVIDER)

# ===============================
# TEST COMMANDS
# ===============================
@bot.command()
async def testjoin(ctx):
    await on_member_join(ctx.author)
    await ctx.send("Simulated join.")

@bot.command()
async def testleave(ctx):
    await on_member_remove(ctx.author)
    await ctx.send("Simulated leave.")

# ===============================
# RUN BOT
# ===============================
if __name__ == "__main__":
    # Start Flask in background thread
    Thread(target=run_web, daemon=True).start()
    # Run Discord bot
    bot.run(os.getenv("DISCORD_TOKEN"))
