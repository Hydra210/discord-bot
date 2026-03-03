require("dotenv").config();
const fs = require("fs");
const path = require("path");

const {
  Client,
  GatewayIntentBits,
  EmbedBuilder,
  REST,
  Routes,
  SlashCommandBuilder
} = require("discord.js");

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers
  ]
});

const DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━";

// Optional fallback URL if no local banner exists
const FALLBACK_BANNER_URL = "https://your-banner-url-if-needed.com/banner.png";

// Detect local banner
const localBannerPath = path.join(__dirname, "banner.png");
const hasLocalBanner = fs.existsSync(localBannerPath);

/* ===============================
   FUNCTION: SEND BANNER
================================ */

async function sendBanner(channel) {
  if (hasLocalBanner) {
    await channel.send({
      files: [localBannerPath]
    });
  } else if (FALLBACK_BANNER_URL) {
    await channel.send({
      content: FALLBACK_BANNER_URL
    });
  }
}

/* ===============================
   JOIN EVENT
================================ */

client.on("guildMemberAdd", async (member) => {
  const channel = member.guild.channels.cache.find(
    c => c.name === "joins"
  );
  if (!channel) return;

  // 1️⃣ Banner
  await sendBanner(channel);

  // 2️⃣ Premium Embed
  const embed = new EmbedBuilder()
    .setColor("#2b2d31")
    .setAuthor({
      name: "Member Joined",
      iconURL: member.user.displayAvatarURL({ dynamic: true })
    })
    .setTitle(`Welcome ${member} to ${member.guild.name}`)
    .setDescription(
      `> Account Created: <t:${Math.floor(member.user.createdTimestamp / 1000)}:R>\n` +
      `> Member Count: **${member.guild.memberCount}**\n` +
      `> User ID: \`${member.id}\``
    )
    .setThumbnail(member.user.displayAvatarURL({ dynamic: true, size: 512 }))
    .setFooter({ text: `${member.guild.name} • New Arrival` })
    .setTimestamp();

  await channel.send({ embeds: [embed] });

  // 3️⃣ Divider
  await channel.send(DIVIDER);
});

/* ===============================
   LEAVE EVENT
================================ */

client.on("guildMemberRemove", async (member) => {
  const channel = member.guild.channels.cache.find(
    c => c.name === "leaves"
  );
  if (!channel) return;

  // 1️⃣ Banner
  await sendBanner(channel);

  // 2️⃣ Leave Embed
  const embed = new EmbedBuilder()
    .setColor("#1e1f22")
    .setAuthor({
      name: "Member Left",
      iconURL: member.user.displayAvatarURL({ dynamic: true })
    })
    .setTitle(`${member.user.username} has left ${member.guild.name}`)
    .setDescription(
      `> Joined: <t:${Math.floor(member.joinedTimestamp / 1000)}:R>\n` +
      `> Members Remaining: **${member.guild.memberCount}**\n` +
      `> User ID: \`${member.id}\``
    )
    .setThumbnail(member.user.displayAvatarURL({ dynamic: true, size: 512 }))
    .setFooter({ text: `${member.guild.name} • Departure Logged` })
    .setTimestamp();

  await channel.send({ embeds: [embed] });

  // 3️⃣ Divider
  await channel.send(DIVIDER);
});

/* ===============================
   SLASH COMMANDS
================================ */

const commands = [
  new SlashCommandBuilder()
    .setName("testjoin")
    .setDescription("Simulate a member joining"),
  new SlashCommandBuilder()
    .setName("testleave")
    .setDescription("Simulate a member leaving")
].map(command => command.toJSON());

client.once("ready", async () => {
  console.log(`Logged in as ${client.user.tag}`);

  const rest = new REST({ version: "10" }).setToken(process.env.DISCORD_TOKEN);

  try {
    await rest.put(
      Routes.applicationCommands(client.user.id),
      { body: commands }
    );
    console.log("Slash commands registered.");
  } catch (error) {
    console.error(error);
  }
});

client.on("interactionCreate", async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const member = interaction.member;

  if (interaction.commandName === "testjoin") {
    client.emit("guildMemberAdd", member);
    await interaction.reply({ content: "Simulated join.", ephemeral: true });
  }

  if (interaction.commandName === "testleave") {
    client.emit("guildMemberRemove", member);
    await interaction.reply({ content: "Simulated leave.", ephemeral: true });
  }
});

/* ===============================
   LOGIN
================================ */

client.login(process.env.DISCORD_TOKEN);
