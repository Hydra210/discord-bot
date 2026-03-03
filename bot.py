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
    
    # ===== ROLES =====
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
    
    # ===== CATEGORIES & CHANNELS =====
    output.append("📁 CATEGORIES & CHANNELS:")
    output.append("-"*50)
    
    for category in guild.categories:
        output.append(f"\n📂 CATEGORY: {category.name}")
        output.append(f"   ID: {category.id}")
        output.append(f"   Position: {category.position}")
        
        # Category permissions
        output.append(f"   PERMISSIONS:")
        for target, overwrite in category.overwrites.items():
            output.append(f"      {target.name}:")
            perms = []
            for perm, value in overwrite:
                if value is not None:
                    perms.append(f"{perm}: {value}")
            output.append(f"         {', '.join(perms)}")
        
        # Channels in category
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
            
            # Channel-specific permissions
            output.append(f"      PERMISSIONS:")
            for target, overwrite in channel.overwrites.items():
                output.append(f"         {target.name}:")
                perms = []
                for perm, value in overwrite:
                    if value is not None:
                        perms.append(f"{perm}: {value}")
                if perms:
                    output.append(f"            {', '.join(perms)}")
            
            # Recent messages (last 5)
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
    
    # Channels not in categories
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
                perms = []
                for perm, value in overwrite:
                    if value is not None:
                        perms.append(f"{perm}: {value}")
                if perms:
                    output.append(f"            {', '.join(perms)}")
    
    output.append("\n" + "="*50 + "\n")
    
    # ===== MEMBERS =====
    output.append("👥 MEMBERS:")
    output.append("-"*50)
    for member in guild.members:
        output.append(f"\nMember: {member.name} ({member.display_name})")
        output.append(f"  ID: {member.id}")
        output.append(f"  Bot: {member.bot}")
        output.append(f"  Joined: {member.joined_at}")
        output.append(f"  Roles: {', '.join([r.name for r in member.roles[1:]])}")  # Skip @everyone
        output.append(f"  Top Role: {member.top_role.name}")
        output.append(f"  Permissions (server-wide): {member.guild_permissions.value}")
    
    output.append("\n" + "="*50 + "\n")
    
    # ===== EMOJIS =====
    output.append("😀 EMOJIS:")
    output.append("-"*50)
    for emoji in guild.emojis:
        output.append(f"  {emoji.name} - ID: {emoji.id} - Animated: {emoji.animated}")
    
    output.append("\n" + "="*50)
    
    # Write to file
    filename = f"server_scan_{guild.id}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    
    # Find the private-bot-cmds channel
    private_channel = discord.utils.get(guild.text_channels, name="private-bot-cmds")
    
    if private_channel:
        # Send to private-bot-cmds
        await private_channel.send(f"✅ Server scan complete! Total lines: {len(output)}", file=discord.File(filename))
        await ctx.send(f"✅ Scan complete! Results sent to {private_channel.mention}")
    else:
        # Fallback to current channel if private-bot-cmds doesn't exist
        await ctx.send(f"⚠️ Could not find #private-bot-cmds channel. Sending here instead.", file=discord.File(filename))
    
    # Clean up
    os.remove(filename)
