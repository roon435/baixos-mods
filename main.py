import discord
from discord.ext import commands
import requests
import random
import string
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Put your token in Railway Variables
ROLE_ID = 1407474526685761586
GAMEPASS_ID = 1454896770

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Roblox Helpers ---
def get_user_id(username: str) -> int:
    url = "https://users.roblox.com/v1/usernames/users"
    try:
        r = requests.post(url, json={"usernames": [username]}, timeout=10)
        print(f"[DEBUG] Username lookup status {r.status_code}, body: {r.text}")
        if r.status_code == 200:
            data = r.json()
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0]["id"]
    except Exception as e:
        print(f"[ERROR] get_user_id failed: {e}")
    return 0

def owns_gamepass(user_id: int, gamepass_id: int) -> bool:
    url = f"https://inventory.roblox.com/v1/users/{user_id}/items/GamePass/{gamepass_id}"
    try:
        r = requests.get(url, timeout=10)
        print(f"[DEBUG] Gamepass check status {r.status_code}, body: {r.text}")
        if r.status_code == 200:
            data = r.json()
            return "data" in data and len(data["data"]) > 0
    except Exception as e:
        print(f"[ERROR] owns_gamepass failed: {e}")
    return False

def generate_code(length: int = 12) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# --- Events ---
@bot.event
async def on_ready():
    print(f"🤖 Bot is ready: {bot.user}")

# --- Commands ---
@bot.command(name="authrblx")
async def authrblx(ctx, username: str):
    await ctx.send(f"🔎 Checking Roblox account **{username}**...")

    user_id = get_user_id(username)
    if not user_id:
        await ctx.send("❌ Invalid Roblox username or Roblox API down. Check logs.")
        return

    if owns_gamepass(user_id, GAMEPASS_ID):
        code = generate_code()
        role = ctx.guild.get_role(ROLE_ID)
        if role:
            await ctx.author.add_roles(role)
        await ctx.send(f"✅ {ctx.author.mention}, you own the gamepass! Your code: **{code}**")
    else:
        await ctx.send("❌ You don’t own the gamepass.")

bot.run(TOKEN)
