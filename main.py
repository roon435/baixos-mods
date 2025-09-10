import os
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")  # Make sure to set this in Railway

# The only channel where the bot is allowed to be used
ALLOWED_CHANNEL_ID = 1414400791518773349  

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.tree.command(name="rblxauth", description="Send your Roblox username")
@app_commands.describe(username="Your Roblox username")
async def rblxauth(interaction: discord.Interaction, username: str):
    # Ensure command is only used in the allowed channel
    if interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message("❌ You can only use this command in the auth channel.", ephemeral=True)
        return

    channel = bot.get_channel(ALLOWED_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("⚠️ Config error: auth channel not found.", ephemeral=True)
        return

    # Send the Roblox username to the channel
    await channel.send(f"✅ **{interaction.user}** submitted Roblox username: `{username}`")

    # Confirm to user privately
    await interaction.response.send_message(f"Your Roblox username `{username}` has been submitted!", ephemeral=True)

bot.run(TOKEN)
