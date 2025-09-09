import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import random
import string
import os

# ---------- CONFIG ----------
TOKEN = os.getenv("DISCORD_TOKEN")  # Your Discord bot token
GUILD_ID = 123456789012345678      # Replace with your server ID
ROLE_ID = 1407474526685761586      # Verified role ID
# ----------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Store codes in memory
temp_codes = {}   # temp_code -> Discord user ID
final_codes = {}  # final_code -> Discord user ID

# -----------------------------
# Helper to generate codes
# -----------------------------
def generate_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

# -----------------------------
# Flask app for Roblox verification
# -----------------------------
app = Flask("DiscordAuthAPI")

@app.route("/verify", methods=["POST"])
def verify_code():
    try:
        data = request.get_json()
        temp_code = data.get("temp_code")
        discord_user = temp_codes.get(temp_code)
        if discord_user:
            return jsonify({"valid": True, "discord_id": discord_user})
        else:
            return jsonify({"valid": False})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Start Flask in separate thread
threading.Thread(target=run_flask).start()

# -----------------------------
# Discord bot events
# -----------------------------
@bot.event
async def on_ready():
    print(f"🤖 Bot ready: {bot.user}")
    guild = discord.Object(id=GUILD_ID)
    try:
        await bot.tree.sync(guild=guild)
        print("✅ Slash commands synced!")
    except Exception as e:
        print("❌ Error syncing commands:", e)

# -----------------------------
# /rblxlink - generate temp code
# -----------------------------
@bot.tree.command(name="rblxlink", description="Start the Roblox verification process")
async def rblxlink(interaction: discord.Interaction):
    code = generate_code()
    temp_codes[code] = interaction.user.id
    await interaction.response.send_message(
        f"🔑 Your temporary Discord code is: **{code}**\nEnter this in the Roblox game GUI.",
        ephemeral=True
    )

# -----------------------------
# /rblxcode - enter final code
# -----------------------------
@bot.tree.command(name="rblxcode", description="Enter the final code from Roblox to get verified")
@app_commands.describe(code="The code you got from Roblox after verification")
async def rblxcode(interaction: discord.Interaction, code: str):
    user_id = final_codes.get(code)
    if user_id == interaction.user.id:
        role = interaction.guild.get_role(ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"✅ Verified {interaction.user.mention}! You now have the role.",
                ephemeral=True
            )
            del final_codes[code]  # remove used code
        else:
            await interaction.response.send_message(
                "⚠️ Role not found. Check ROLE_ID.",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "❌ Invalid or expired code.",
            ephemeral=True
        )

# -----------------------------
# Temporary admin command to add final codes (simulate Roblox game)
# -----------------------------
@bot.tree.command(name="addfinalcode", description="Admin: add a final code for testing")
@app_commands.describe(code="Code to add", user="User ID to assign")
async def addfinalcode(interaction: discord.Interaction, code: str, user: int):
    final_codes[code] = user
    await interaction.response.send_message(f"Added final code `{code}` for user ID `{user}`.", ephemeral=True)

# Run the bot
bot.run(TOKEN)
