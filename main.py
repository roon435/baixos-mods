import os
import discord
from discord.ext import commands
import requests
import random
import string

# Enable intents to assign roles
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Roblox Game Pass ID
GAMEPASS_ID = 1454896770  # Your Game Pass

# Discord role ID (replace with your role ID in Discloud environment variable)
ROLE_ID = int(os.environ.get("ROLE_ID"))

# Store linked users: discord_id -> {username, code}
linked_users = {}

# Function to generate random code
def generate_random_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Function to check Game Pass ownership via Roblox API
def check_gamepass(username: str):
    # Get Roblox userId
    response = requests.get(f"https://api.roblox.com/users/get-by-username?username={username}")
    if response.status_code != 200:
        return False, None
    data = response.json()
    if "Id" not in data or data["Id"] == 0:
        return False, None
    user_id = data["Id"]

    # Check Game Pass ownership
    gp_response = requests.get(f"https://apis.roblox.com/ownership/v1/users/{user_id}/assets/collectibles?assetIds={GAMEPASS_ID}")
    if gp_response.status_code != 200:
        return False, None
    gp_data = gp_response.json()
    if gp_data.get("data") and len(gp_data["data"]) > 0:
        return True, user_id
    return False, user_id

# Slash command for linking Roblox account
@bot.slash_command(name="usernameauth", description="Link your Roblox account via Game Pass")
async def usernameauth(ctx, username: str):
    await ctx.defer()
    owns, user_id = check_gamepass(username)
    if owns:
        code = generate_random_code()
        linked_users[ctx.author.id] = {"username": username, "code": code}
        
        # Assign role
        role = ctx.guild.get_role(ROLE_ID)
        if role:
            await ctx.author.add_roles(role)
        
        await ctx.respond(f"✅ {username} owns the Game Pass! You have been linked and given the role. Your code: `{code}`")
    else:
        await ctx.respond(f"❌ {username} does NOT own the Game Pass.")

# Run bot with token from environment variable
bot.run(os.environ["DISCORD_TOKEN"])
