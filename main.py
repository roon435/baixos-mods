import discord
from discord.ext import commands
import requests
import random
import string
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # put your token in Railway variables
ROLE_ID = 1407474526685761586       # role ID you gave me
GAMEPASS_ID = 1454896770            # your gamepass ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ New Roblox API for username -> userId
def get_user_id(username: str) -> int:
    url = "https://users.roblox.com/v1/usernames/users"
    response = requests.post(url, json={"usernames": [username]})
    if response.status_code == 200:
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["id"]
    return 0

# ✅ Check if user owns gamepass
def owns_gamepass(user_id: int, gamepass_id: int) -> bool:
    url = f"https://inventory.roblox.com/v1/users/{user_id}/items/GamePass/{gamepass_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return "data" in data and len(data["data"]) > 0
    return False

# ✅ Generate random code
def generate_code(length: int = 12) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@bot.event
async def on_ready():
    print(f"🤖 Bot is ready: {bot.user}")

@bot.command(name="authrblx")
async def authrblx(ctx, username: str):
    await ctx.send(f"🔎 Checking Roblox account **{username}**...")

    user_id = get_user_id(username)
    if not user_id:
        await ctx.send("❌ Invalid Roblox username.")
        return

    if owns_gamepass(user_id, GAMEPASS_ID):
        code = generate_code()
        role = ctx.guild.get_role(ROLE_ID)
        if role:
            await ctx.author.add_roles(role)
        await ctx.send(f"✅ {ctx.author.mention}, you own the gamepass! Here is your code: **{code}**")
    else:
        await ctx.send("❌ You don’t own the gamepass.")

bot.run(TOKEN)
