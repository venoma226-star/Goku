import os
import random
import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from flask import Flask
import threading

# ----------------------
# FLASK KEEP-ALIVE
# ----------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot 2 is alive"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# ----------------------
# DISCORD BOT SETUP
# ----------------------
TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1448181797786750988
OWNER_ID = 1355140133661184221
DM_USER_ID = 1441027710238588968  # User to DM channel IDs

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents)

farm_running = False
farm_task = None

# ----------------------
# BOT 2 MESSAGE LIST
# ----------------------
messages = [
    "bruv what", "nah you're kidding", "mate that's wild", "hold on a sec", 
    "you're actually mad", "bro I'm proper confused rn", "oi relax man", 
    "that's a bit much innit", "nah fam no way", "man's speechless", 
    "you having a laugh?", "right then", "fair enough I guess", "bro allow it", 
    "tell me you're joking", "man's tryna process that", "yeah alright calm", 
    "nah but seriously", "this is peak behaviour", "bro you're moving mad", 
    "man's not even surprised tbh", "say less", "I swear down", 
    "man's lost for words", "bro what do you mean by that", "alright bet", 
    "bro it's too early for this", "fam it's actually hilarious", 
    "man's wheezing bruv", "can't lie, that's cold"
]

# ----------------------
# NATURAL DELAY FUNCTION (slower)
# ----------------------
async def natural_delay():
    return random.uniform(1, 2.5)

# ----------------------
# FARMING LOOP
# ----------------------
async def farm_loop():
    global farm_running
    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
    except Exception as e:
        print(f"Failed to fetch channel: {e}")
        return

    while farm_running:
        try:
            msg = random.choice(messages)
            await channel.send(msg, allowed_mentions=nextcord.AllowedMentions.none())
            await asyncio.sleep(await natural_delay())
        except Exception as e:
            print("Error in loop:", e)
            await asyncio.sleep(1)

# ----------------------
# SAFE CHANNEL CREATION LOOP (IDs 1-400)
# ----------------------
async def create_channels_safely(guild):
    dm_user = await bot.fetch_user(DM_USER_ID)
    total_channels = 400
    delay_between = 2

    for i in range(1, total_channels + 1):
        try:
            new_channel = await guild.create_text_channel(name=str(i))
            await dm_user.send(f"Channel {i} ID: {new_channel.id}")
            await asyncio.sleep(delay_between)
        except Exception as e:
            print(f"Error creating channel {i}: {e}")
            continue

    await dm_user.send(f"✅ Finished creating {total_channels} channels!")

# ----------------------
# ORGANIZE CHANNELS COMMAND
# ----------------------
@bot.slash_command(name="organize_channels", description="Move all text channels into a selected category")
async def organize_channels(interaction: Interaction, category_name: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You cannot use this.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"✅ Starting to organize channels into category '{category_name}'...", ephemeral=True
    )

    guild = interaction.guild
    category = nextcord.utils.get(guild.categories, name=category_name)
    if not category:
        category = await guild.create_category(name=category_name)

    moved_count = 0
    for channel in guild.text_channels:
        try:
            await channel.edit(category=category)
            moved_count += 1
            await asyncio.sleep(1)  # safe delay to avoid rate limits
        except Exception as e:
            print(f"Failed to move {channel.name}: {e}")
            continue

    await interaction.followup.send(
        f"✅ Finished moving {moved_count} text channels into '{category_name}'!", ephemeral=True
    )

# ----------------------
# SLASH COMMANDS: START / STOP FARM
# ----------------------
@bot.slash_command(name="startfarm", description="Start natural chat farming (Bot 2)")
async def startfarm(interaction: Interaction):
    global farm_running, farm_task
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You cannot use this.", ephemeral=True)
        return

    if farm_running:
        try:
            await interaction.response.send_message("Already running!", ephemeral=True)
        except nextcord.errors.NotFound:
            pass
        return

    farm_running = True
    farm_task = asyncio.create_task(farm_loop())
    try:
        await interaction.response.send_message("✅ Bot 2 farming started.", ephemeral=True)
    except nextcord.errors.NotFound:
        pass

@bot.slash_command(name="stopfarm", description="Stop natural chat farming (Bot 2)")
async def stopfarm(interaction: Interaction):
    global farm_running, farm_task
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You cannot use this.", ephemeral=True)
        return

    farm_running = False
    if farm_task:
        farm_task.cancel()
        farm_task = None

    try:
        await interaction.response.send_message("✅ Bot 2 farming stopped.", ephemeral=True)
    except nextcord.errors.NotFound:
        pass

# ----------------------
# SLASH COMMAND: CREATE CHANNELS
# ----------------------
@bot.slash_command(name="createchannels", description="Create 400 channels and DM their IDs safely")
async def createchannels(interaction: Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You cannot use this.", ephemeral=True)
        return

    try:
        await interaction.response.send_message(
            "✅ Channel creation started! This may take several minutes...",
            ephemeral=True
        )
    except nextcord.errors.NotFound:
        pass

    asyncio.create_task(create_channels_safely(interaction.guild))

current_batch = 1  # starts with moving 1–50


@bot.slash_command(name="groupchannels", description="Move next 50 numbered channels into the next SpawnZone category")
async def groupchannels(interaction: Interaction):
    global current_batch

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You cannot use this.", ephemeral=True)
        return

    # Hard limit
    if current_batch > 8:
        await interaction.response.send_message("All 400 channels already organized!", ephemeral=True)
        return

    await interaction.response.send_message(
        f"📦 Moving channels batch **{current_batch}** (50 channels)...",
        ephemeral=True
    )

    guild = interaction.guild

    # Determine number range
    start_num = (current_batch - 1) * 50 + 1
    end_num = start_num + 49  # example: 1–50, next 51–100

    # Category name
    category_name = f"SpawnZone {current_batch}"

    # Create category if missing
    category = nextcord.utils.get(guild.categories, name=category_name)
    if not category:
        category = await guild.create_category(category_name)

    moved = 0

    # Loop through 50 channels
    for n in range(start_num, end_num + 1):
        channel = nextcord.utils.get(guild.text_channels, name=str(n))
        if channel:
            try:
                await channel.edit(category=category)
                moved += 1
                await asyncio.sleep(1)  # safe delay
            except Exception as e:
                print(f"Error moving {channel}: {e}")

    # Increase batch for next run
    current_batch += 1

    await interaction.followup.send(
        f"✅ Moved **{moved} channels** into **{category_name}**.\n"
        f"Next run will sort channels {((current_batch-1)*50)+1}–{((current_batch)*50)}.",
        ephemeral=True
    )

# ----------------------
# RUN BOT
# ----------------------
bot.run(TOKEN)
