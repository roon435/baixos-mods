import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import random
import string
import os

# ---------- CONFIG ----------
TOKEN = os.environ.get("DISCORD_TOKEN")  # Discord bot token
GUILD_ID = 123456789012345678           # Replace with your Discord server ID
ROLE_ID = 1407474526685761586           # Verified role ID
# ----------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Store codes in memory
temp_codes = {}   # temp_code -> Discord user ID
final_codes = {}  # final_code -> Discord user ID

# -----------------------------
# Helper to generate random codes
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
    port = int(os.environ.get("PORT", 8080))  # Railway provides $PORT
    app.run(host="0.0.0.0", port=port, threaded=True)

# Start Flask in a separate thread
threading.Thread(target=run_flask).start()

# -----------------------------
# Discord bot events
# -----------------------------
@bot.event
async def on_ready():
    print(f"🤖 Bot ready: {bot.user}")

# -----------------------------
# !rblxlink - generate temp code
# -----------------------------
@bot.command(name="rblxlink")
async def rblxlink(ctx):
    code = generate_code()
    temp_codes[code] = ctx.author.id
    await ctx.author.send(
        f"🔑 Your temporary Discord code is: **{code}**\n"
        "Enter this in the Roblox game GUI."
    )
    await ctx.send(f"✅ {ctx.author.mention}, I sent you a DM with your Discord code.", delete_after=5)

# -----------------------------
# !rblxcode - enter final code
# -----------------------------
@bot.command(name="rblxcode")
async def rblxcode(ctx, code: str):
    user_id = final_codes.get(code)
    if user_id == ctx.author.id:
        role = ctx.guild.get_role(ROLE_ID)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"✅ Verified {ctx.author.mention}! You now have the role.", delete_after=10)
            del final_codes[code]  # remove used code
        else:
            await ctx.send("⚠️ Role not found. Check ROLE_ID.", delete_after=10)
    else:
        await ctx.send("❌ Invalid or expired code.", delete_after=10)

# -----------------------------
# !addfinalcode - admin only
# -----------------------------
@bot.command(name="addfinalcode")
async def addfinalcode(ctx, code: str, user: int):
    final_codes[code] = user
    await ctx.send(f"Added final code `{code}` for user ID `{user}`.", delete_after=10)

# Run the Discord bot
bot.run(TOKEN)
