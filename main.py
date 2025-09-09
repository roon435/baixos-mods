import os
import random
import discord
from discord.ext import commands
from discord import app_commands
import requests

# --- CONFIG ---
ROLE_ID = 1407474526685761586
GAMEPASS_ID = 1454896770  # Your Game Pass ID
GUILD_ID = None  # put your server ID here for faster slash command sync

# --- INTENTS ---
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

# --- BOT ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- HELPER FUNCTION ---
def owns_gamepass(user_id: int) -> bool:
    url = f"https://inventory.roblox.com/v1/users/{user_id}/items/GamePass/{GAMEPASS_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return "data" in data and len(data["data"]) > 0
    return False

def get_user_id(username: str) -> int:
    url = f"https://api.roblox.com/users/get-by-username?username={username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("Id", 0)
    return 0

# --- EVENTS ---
@bot.event
async def on_ready():
    try:
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            await bot.tree.sync(guild=guild)
        else:
            await bot.tree.sync()
        print(f"✅ Logged in as {bot.user}")
    except Exception as e:
        print(f"Slash sync error: {e}")

# --- COMMAND ---
@bot.tree.command(name="usernameauth", description="Link your Roblox account with username.")
@app_commands.describe(username="Your Roblox username")
async def usernameauth(interaction: discord.Interaction, username: str):
    await interaction.response.defer(thinking=True)

    # Get Roblox user ID
    user_id = get_user_id(username)
    if not user_id:
        await interaction.followup.send("❌ Invalid Roblox username.")
        return

    # Check ownership
    if not owns_gamepass(user_id):
        await interaction.followup.send("❌ You don't own the Game Pass required.")
        return

    # Give role
    role = interaction.guild.get_role(ROLE_ID)
    if not role:
        await interaction.followup.send("⚠️ Role not found on this server.")
        return

    try:
        await interaction.user.add_roles(role)
        code = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        await interaction.followup.send(f"✅ Authenticated! Here is your code: **{code}**")
    except discord.Forbidden:
        await interaction.followup.send("⚠️ I don't have permission to give roles.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {e}")

# --- START BOT ---
bot.run(os.environ["DISCORD_TOKEN"])
