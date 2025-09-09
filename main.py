import discord
from discord.ext import commands
import random
import string
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # put your token in Railway environment variables
ROLE_ID = 1407474526685761586

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# temporary storage: final codes (from Roblox) -> Discord user ID
final_codes = {}

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@bot.event
async def on_ready():
    print(f"🤖 Bot is ready: {bot.user}")

# Step 1: User starts link process (optional)
@bot.command()
async def rblxlink(ctx):
    code = generate_code()
    final_codes[code] = ctx.author.id
    await ctx.send(f"🔑 Your temporary link code is: **{code}**\nGo to the Roblox game and enter this code.")

# Step 2: User enters final code from Roblox
@bot.command()
async def rblxcode(ctx, code: str):
    # Check if code exists in memory
    user_id = final_codes.get(code)
    if user_id == ctx.author.id:
        role = ctx.guild.get_role(ROLE_ID)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"✅ Verified {ctx.author.mention}! You now have the role.")
            del final_codes[code]  # remove used code
        else:
            await ctx.send("⚠️ Role not found. Please check ROLE_ID.")
    else:
        await ctx.send("❌ Invalid or expired code.")
        
bot.run(TOKEN)
