import discord
from discord import app_commands
from discord.ext import commands
import random
import string
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Your bot token
GUILD_ID = 123456789012345678  # Replace with your server ID
ROLE_ID = 1407474526685761586  # Your verified role

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Store final codes: code -> Discord user ID
final_codes = {}

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@bot.event
async def on_ready():
    print(f"🤖 Bot is ready: {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        await bot.tree.sync(guild=guild)
        print("✅ Slash commands synced!")
    except Exception as e:
        print("Error syncing commands:", e)

# -----------------------------
# Slash command: /rblxlink
# -----------------------------
@bot.tree.command(name="rblxlink", description="Start the Roblox verification process")
async def rblxlink(interaction: discord.Interaction):
    code = generate_code()
    final_codes[code] = interaction.user.id
    await interaction.response.send_message(
        f"🔑 Your temporary link code is: **{code}**\nGo to the Roblox game and enter this code.",
        ephemeral=True
    )

# -----------------------------
# Slash command: /rblxcode
# -----------------------------
@bot.tree.command(name="rblxcode", description="Enter the final code from Roblox")
@app_commands.describe(code="Enter the code you got from Roblox")
async def rblxcode(interaction: discord.Interaction, code: str):
    user_id = final_codes.get(code)
    if user_id == interaction.user.id:
        role = interaction.guild.get_role(ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Verified {interaction.user.mention}! You now have the role.", ephemeral=True)
            del final_codes[code]  # remove used code
        else:
            await interaction.response.send_message("⚠️ Role not found. Please check ROLE_ID.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Invalid or expired code.", ephemeral=True)

bot.run(TOKEN)
