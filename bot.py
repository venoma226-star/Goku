import os
import random
import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from flask import Flask

# ----------------------
# FLASK KEEP-ALIVE
# ----------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot 2 is alive"

# Run Flask in background
import threading
def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()


# ----------------------
# DISCORD BOT SETUP
# ----------------------
TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1448207122352570501
OWNER_ID = 1355140133661184221

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents)

farm_running = False
farm_task = None


# ----------------------
# BOT 2 MESSAGE LIST
# ----------------------
messages = [
    "bruv what",
    "nah you're kidding",
    "mate that's wild",
    "hold on a sec",
    "you're actually mad",
    "bro I'm proper confused rn",
    "oi relax man",
    "that's a bit much innit",
    "nah fam no way",
    "man's speechless",
    "you having a laugh?",
    "right then",
    "fair enough I guess",
    "bro allow it",
    "tell me you're joking",
    "man's tryna process that",
    "yeah alright calm",
    "nah but seriously",
    "this is peak behaviour",
    "bro you're moving mad",
    "man's not even surprised tbh",
    "say less",
    "I swear down",
    "man's lost for words",
    "bro what do you mean by that",
    "alright bet",
    "bro it's too early for this",
    "fam it's actually hilarious",
    "man's wheezing bruv",
    "can't lie, that's cold"
]


# ----------------------
# NATURAL DELAY FUNCTION
# ----------------------
async def natural_delay():
    # Random realistic human-like timing
    return random.uniform(0.3, 1.4)


# ----------------------
# FARMING LOOP
# ----------------------
async def farm_loop():
    global farm_running
    channel = bot.get_channel(CHANNEL_ID)

    while farm_running:
        try:
            msg = random.choice(messages)
            await channel.send(msg)
            await asyncio.sleep(await natural_delay())
        except Exception as e:
            print("Error in loop:", e)
            await asyncio.sleep(1)


# ----------------------
# SLASH COMMAND SETUP
# ----------------------
@bot.event
async def on_ready():
    print(f"Bot 2 logged in as {bot.user}")


@bot.slash_command(name="startfarm", description="Start natural chat farming (Bot 2)")
async def startfarm(interaction: Interaction):
    global farm_running, farm_task

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You cannot use this.", ephemeral=True)
        return

    if farm_running:
        await interaction.response.send_message("Already running!", ephemeral=True)
        return

    farm_running = True
    farm_task = asyncio.create_task(farm_loop())
    await interaction.response.send_message("Bot 2 farming started.", ephemeral=True)


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

    await interaction.response.send_message("Bot 2 farming stopped.", ephemeral=True)


# ----------------------
# RUN BOT
# ----------------------
bot.run(TOKEN)
