import discord
from discord.ext import commands
import requests
import random
import string
import os

# --- CONFIG ---
TOKEN = os.getenv("DISCORD_TOKEN")  # set in Railway Variables
ROLE_ID = 1407474526685761586       # role to give when verified
GAMEPASS_ID = 1454896770            # Baixos-Authenticator gamepass ID
ALLOWED_CHANNEL_ID = 1414400791518773349  # only allow in this channel

# --- DISCORD SETUP ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- ROBLOX HELPERS ---
def get_user_id(username: str) -> int:
    """Convert Roblox username -> userId"""
    url = "https://users.roblox.com/v1/usernames/users"
    try:
        r = requests.post(url, json={"usernames": [username]}, timeout=10)
        print(f"[DEBUG] Username lookup {r.status_code}: {r.text[:200]}...")
        if r.status_code == 200:
            data = r.json()
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0]["id"]
    except Exception as e:
        print(f"[ERROR] get_user_id failed: {e}")
    return 0

def owns_gamepass(user_id: int, gamepass_id: int) -> bool:
    """Check ownership via Roblox Marketplace API"""
    url = f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass_id}/users/{user_id}/ownership"
    try:
        r = requests.get(url, timeout=10)
        print(f"[DEBUG] Marketplace check {r.status_code}: {r.text[:200]}...")
        if r.status_code == 200:
            data = r.json()
            return data.get("ownership", False)
    except Exception as e:
        print(f"[ERROR] owns_gamepass failed: {e}")
    return False

def generate_code(length: int = 12) -> str:
    """Generate a random alphanumeric code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"🤖 Bot is ready: {bot.user}")

# --- COMMAND ---
@bot.command(name="authrblx")
async def authrblx(ctx, username: str):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("❌ This command can only be used in the designated channel.")
        return

    await ctx.send(f"🔎 Checking Roblox account **{username}**...")

    user_id = get_user_id(username)
    if not user_id:
        await ctx.send("❌ Invalid Roblox username or Roblox API down. Check logs.")
        return

    if owns_gamepass(user_id, GAMEPASS_ID):
        code = generate_code()
        role = ctx.guild.get_role(ROLE_ID)
        if role:
            try:
                await ctx.author.add_roles(role)
            except discord.Forbidden:
                await ctx.send("⚠️ I don't have permission to assign roles.")
        # DM the code to the user
        try:
            await ctx.author.send(f"✅ You own the Baixos-Authenticator gamepass! Your code: **{code}**")
            await ctx.send(f"✅ {ctx.author.mention}, check your DMs for your code!")
        except discord.Forbidden:
            await ctx.send(f"⚠️ {ctx.author.mention}, I couldn't DM you. Make sure your DMs are open.")
    else:
        await ctx.send("❌ You don’t own the Baixos-Authenticator gamepass.")

# --- RUN BOT ---
bot.run(TOKEN)
