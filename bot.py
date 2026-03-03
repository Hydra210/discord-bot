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
    
    # 2 Welcome Embed
    embed = discord.Embed(
        title=f"🎉 Welcome to {member.guild.name}!",
        description=f"Hey {member.mention}! We're glad you're here. Make yourself at home!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name="👋 You're our member #",
        value=str(member.guild.member_count),
        inline=True
    )
    embed.add_field(
        name="📅 Account Age",
        value=f"<t:{int(member.created_at.timestamp())}:R>",
        inline=True
    )
    embed.set_footer(text=f"Welcome aboard! • {member.guild.name}", icon_url=member.guild.icon.url if member.guild.icon else None)
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
    
    # 2 Goodbye Embed
    embed = discord.Embed(
        title=f"👋 {member.name} has left",
        description=f"We'll miss you! Thanks for being part of {member.guild.name}.",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    
    if member.joined_at:
        embed.add_field(
            name="⏱️ Time with us",
            value=f"Joined <t:{int(member.joined_at.timestamp())}:R>",
            inline=True
        )
    
    embed.add_field(
        name="👥 Members now",
        value=str(member.guild.member_count),
        inline=True
    )
    
    embed.set_footer(text=f"Goodbye! • {member.guild.name}", icon_url=member.guild.icon.url if member.guild.icon else None)
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
# SHUTDOWN COMMAND (OWNER ONLY)
# ===============================
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("🔴 Shutting down bot... See you soon!")
    await bot.close()

# ===============================
# RUN BOT
# ===============================
if __name__ == "__main__":
    # Start Flask in background thread
    Thread(target=run_web, daemon=True).start()
    # Run Discord bot
    bot.run(os.getenv("DISCORD_TOKEN"))
