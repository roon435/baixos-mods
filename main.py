import os
import random
import discord
from discord.ext import commands
import requests

# --- CONFIG ---
ROLE_ID = 1407474526685761586
GAMEPASS_ID = 1454896770  # Your Game Pass ID

# --- INTENTS ---
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True  # ✅ REQUIRED for ! commands

# --- BOT ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- HELPER FUNCTIONS ---
def owns_gamepass(user_id: int) -> bool:
    """Check if a Roblox user owns your gamepass."""
    url = f"https://inventory.roblox.com/v1/users/{user_id}/items/GamePass/{GAMEPASS_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return "data" in data and len(data["data"]) > 0
    return False

def get_user_id(username: str) -> int:
    """Convert a Roblox username to user ID."""
    url = f"https://api.roblox.com/users/get-by-username?username={username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("Id", 0)
    return 0

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"🤖 Bot is ready: {bot.user}")

# --- COMMANDS ---
@bot.command(name="authrblx")
async def authrblx(ctx, username: str = None):
    print(f"📩 Command received from {ctx.author}: {ctx.message.content}")

    if not username:
        await ctx.send("⚠️ Usage: `!authrblx <YourRobloxName>`")
        return

    await ctx.send(f"🔎 Checking Roblox account **{username}**...")

    # Get Roblox user ID
    user_id = get_user_id(username)
    if not user_id:
        await ctx.send("❌ Invalid Roblox username.")
        return

    # Check ownership
    if not owns_gamepass(user_id):
        await ctx.send("❌ You don't own the Baixo's Authenticator game pass.")
        return

    # Give role
    role = ctx.guild.get_role(ROLE_ID)
    if not role:
        await ctx.send("⚠️ Role not found on this server.")
        return

    try:
        await ctx.author.add_roles(role)
        code = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        await ctx.send(f"✅ Authenticated as **{username}**!\nHere is your code: **{code}**")
    except discord.Forbidden:
        await ctx.send("⚠️ I don't have permission to give roles.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")

# --- START BOT ---
bot.run(os.environ["DISCORD_TOKEN"])
