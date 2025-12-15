import os
import nextcord
from nextcord.ext import commands, tasks
from nextcord import Interaction, SlashOption
from flask import Flask
import threading
import sqlite3
from datetime import datetime, time, timedelta
import pytz

# =============================
# CONFIG
# =============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = os.getenv("DB_FILE", "qotd.db")
PORT = int(os.getenv("PORT", 8080))

QOTD_CHANNEL_ID = 1432548795488669747
QOTD_ROLE_ID = 1432549046781739089
IST = pytz.timezone("Asia/Kolkata")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

# =============================
# BOT
# =============================
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =============================
# FLASK (UPTIME)
# =============================
app = Flask("")

@app.route("/")
def home():
    return "QOTD Bot Alive"

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

threading.Thread(target=run_flask).start()

# =============================
# DATABASE
# =============================
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS qotd_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current_index INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS qotd_embed (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    line TEXT,
    title TEXT,
    description TEXT,
    footer TEXT,
    footer_icon TEXT,
    image TEXT,
    thumbnail TEXT,
    color INTEGER
)
""")

c.execute("INSERT OR IGNORE INTO qotd_state VALUES (1, 0)")
conn.commit()

# =============================
# QOTD QUESTIONS (1–250, fully mixed)
# =============================
QOTD_QUESTIONS = [
"What emotion have you been feeling the most lately?",
"What is something you would love to eat every day and never get bored of?",
"What moment changed you the most as a person?",
"What is the best thing you’ve ever done for your partner?",
"What is a small thing that makes your day better?",
"What is a skill you wish you could instantly master?",
"What do you value most in your friendships?",
"What song never fails to make you smile?",
"What fear have you overcome recently?",
"If you could live anywhere in the world, where would it be?",
"What is your go-to comfort food?",
"What keeps you motivated on hard days?",
"What is a habit you want to break?",
"What is one thing you’re proud of but rarely talk about?",
"What is your favorite childhood memory?",
"What is something you secretly enjoy?",
"What is the most random fact about yourself?",
"What does happiness feel like for you?",
"What is the boldest thing you’ve done for love?",
"What is a small win you had this week?",
"What is a random act of kindness you remember?",
"What is your favorite way to relax after a long day?",
"What is one thing you would tell your younger self?",
"What is your love language?",
"What does loyalty mean to you?",
"If today had a theme song, what would it be?",
"What makes you feel truly alive?",
"What is one thing you want to improve about yourself?",
"What is a fear you still want to conquer?",
"What is your favorite snack?",
"What is something that instantly lifts your mood?",
"What is the best advice you’ve ever received?",
"What is something people often misunderstand about you?",
"What is the weirdest food combination you enjoy?",
"What is a compliment you remember vividly?",
"What is your favorite time of the day and why?",
"What is one thing that makes you feel appreciated?",
"What is a small pleasure that makes you happy?",
"What is a habit you want to develop?",
"What does peace feel like to you?",
"What is a quality you find most attractive in others?",
"What is your favorite way to spend a weekend?",
"What is a lesson you learned from failure?",
"What is your favorite movie or series of all time?",
"What is something you procrastinate on the most?",
"What is one thing you want to forgive yourself for?",
"What is the best gift you’ve ever received?",
"What is your favorite drink or beverage?",
"What is a skill everyone should learn?",
"What is your happiest memory with friends?",
"What is the boldest decision you’ve ever made?",
"What is a challenge that made you stronger?",
"What is one thing you’d change about the past if you could?",
"What is your favorite place to go when you want to think?",
"What is a dream you still want to achieve?",
"What is something you’ve learned about yourself this year?",
"What is your favorite way to celebrate success?",
"What makes you feel safe?",
"What is one thing that makes you anxious?",
"What is a habit that helps you stay organized?",
"What is something you’re grateful for today?",
"What is a random thing that makes you laugh?",
"What is one thing you want to do differently tomorrow?",
"What is your favorite dessert?",
"What is a quality you admire in others?",
"What is the best trip you’ve ever taken?",
"What is a moment that made you feel proud?",
"What is a skill you’re currently working on?",
"What is one thing you would like to unlearn?",
"What is a decision you are most proud of?",
"What is one thing you would like to learn this month?",
"What is a goal you have for personal growth?",
"What is your favorite type of music or artist?",
"What is something that recently inspired you?",
"What is a fear you want to face this year?",
"What is your favorite quote or saying?",
"What is something that makes you feel nostalgic?",
"What is one habit that makes your life better?",
"What is a personal achievement you’re proud of?",
"What is something that makes you feel creative?",
"What is a favorite hobby or pastime?",
"What is a memory that makes you smile every time?",
"What is something you’ve recently discovered about yourself?",
"What is one thing you enjoy doing alone?",
"What is a topic you love to discuss with friends?",
"What is something that challenges your thinking?",
"What is a small act that makes a big difference to you?",
"What is a memory you cherish from school days?",
"What is something that gives you hope?",
"What is your favorite way to unwind in the evening?",
"What is a lesson you learned from a difficult situation?",
"What is a habit that improves your mental health?",
"What is something you want to teach someone else?",
"What is one thing that always cheers you up?",
"What is a skill you admire in others?",
"What is a goal you have for this month?",
"What is your favorite way to express yourself?",
"What is something you would like to do more often?",
"What is your favorite time of the year?",
"What is one thing you wish people knew about you?",
"What is a habit that you want to start next week?",
"What is something that makes you feel connected to others?",
"What is a decision you made that changed your perspective?",
"What is one way you express gratitude daily?",
"What is a dream you had as a child?",
"What is your favorite outdoor activity?",
"What is a topic you are passionate about?",
"What is something that motivates you each morning?",
"What is a mistake that taught you the most?",
"What is a moment you felt truly happy?",
"What is a challenge you are proud to have overcome?",
"What is one thing you would like to simplify in your life?",
"What is a place you want to visit this year?",
"What is your favorite form of exercise?",
"What is a book that had a big impact on you?",
"What is something that makes you feel accomplished?",
"What is a personal strength you rely on?",
"What is a tradition that is meaningful to you?",
"What is a habit that helps you stay focused?",
"What is one thing you would like to spend more time on?",
"What is a lesson you learned from a friendship?",
"What is something you want to explore creatively?",
"What is a memory that always makes you laugh?",
"What is a small thing that brings you joy daily?",
"What is one way you relax after stress?",
"What is a personal value that guides your actions?",
"What is a skill you want to master this year?",
"What is one thing you love about your personality?",
"What is a recent achievement you’re proud of?",
"What is a moment you want to remember forever?",
"What is a personal project you’re working on?",
"What is one way you challenge yourself regularly?",
"What is a decision you made that improved your life?",
"What is a favorite meal or dish you enjoy?",
"What is something that inspires you daily?",
"What is one thing you do to stay mindful?",
"What is a conversation that had a lasting impact on you?",
"What is a habit that makes your day better?",
"What is something you want to learn from someone else?",
"What is a way you practice self-care?",
"What is a challenge you are preparing for?",
"What is a place that makes you feel peaceful?",
"What is something that motivates you when you’re down?",
"What is one thing you do to help others?",
"What is a topic you enjoy reading about?",
"What is something that makes you feel confident?",
"What is one thing you would change in your routine?",
"What is a way you celebrate small successes?",
"What is a skill that you use daily?",
"What is a hobby you want to develop further?",
"What is a choice that changed your life significantly?",
"What is something that brings laughter to your day?",
"What is a goal you’re working towards right now?",
"What is a memory that gives you comfort?",
"What is something you admire in your family?",
"What is a way you connect with nature?",
"What is something you want to accomplish this week?",
"What is a personal mantra or motto you follow?",
"What is a way you overcome fear?",
"What is something you enjoy about your daily routine?",
"What is a moment you felt truly understood?",
"What is a goal you set for yourself last year?",
"What is one thing that makes you feel relaxed?",
"What is a person who influenced your life positively?",
"What is something you’d like to do for fun soon?",
"What is a personal challenge you are working on?",
"What is a way you give back to your community?",
"What is one thing that reminds you to be grateful?",
"What is a memory that makes you feel warm inside?",
"What is something that gives you energy?",
"What is a dream you want to achieve this year?",
"What is something you do that makes you feel happy?",
"What is one thing that encourages you when you’re down?",
"What is a small tradition that you enjoy?",
"What is a lesson you learned recently?",
"What is something that motivates you creatively?",
"What is one thing you want to improve in yourself?",
"What is a way you make someone else’s day better?",
"What is a place that inspires you?",
"What is one thing you are curious about?",
"What is a goal you want to accomplish this month?",
"What is a habit you want to continue?",
"What is something that surprises you about yourself?",
"What is a way you reflect on your day?",
"What is something you want to experience at least once?",
"What is a personal rule you follow?",
"What is a skill you admire in someone else?",
"What is one thing you want to celebrate today?",
"What is something you want to create?",
"What is a way you practice patience?",
"What is a habit that keeps you grounded?",
"What is something that makes you feel loved?",
"What is a moment that made you feel proud of yourself?",
"What is a dream you are working towards?",
"What is something that helps you focus?",
"What is one thing that you would like to simplify?",
"What is a choice you made that you’re proud of?",
"What is a way you express kindness?",
"What is a moment that brought you joy unexpectedly?",
"What is a habit that improves your mood?",
"What is something you are learning right now?",
"What is a personal strength you want to develop further?",
"What is a topic that fascinates you?",
"What is a way you stay positive?",
"What is a decision that made your life better?",
"What is one thing you enjoy about yourself?",
"What is something that inspires confidence in you?",
"What is a lesson you want to remember forever?",
"What is a small goal you want to achieve this week?",
"What is a place that makes you happy?",
"What is one thing you do to maintain balance?",
"What is a way you challenge yourself mentally?",
"What is a recent act of kindness you appreciated?",
"What is something that makes you feel calm?",
"What is a goal you want to achieve this year?",
"What is a memory that always makes you smile?",
"What is something you enjoy doing with friends?",
"What is a hobby that brings you joy?",
"What is something you are proud of learning recently?",
"What is one way you express gratitude?",
"What is a place you’d love to visit someday?",
"What is a personal value you always try to uphold?",
"What is one thing you’ve done recently that challenged you?",
"What is a dream you’ve had since childhood?",
"What is a way you unwind after a busy day?",
"What is something that motivates you to improve?",
"What is one thing that brings you peace?",
"What is a skill you are proud of?",
"What is a personal rule that helps you succeed?",
"What is something that you enjoy about your daily routine?",
"What is a memory that gives you strength?",
"What is one thing you want to accomplish soon?",
"What is a habit that you want to build this month?",
"What is something that brings excitement to your day?",
"What is one thing you are curious to learn more about?",
"What is a way you support someone else?",
"What is a lesson you want to pass on?",
"What is a goal you are working towards currently?",
"What is something that makes you feel content?",
"What is a moment that changed your perspective?",
"What is one thing you want to do differently next week?",
"What is a small act of kindness you can do today?",
"What is something that inspires creativity in you?",
"What is a dream you are planning to achieve?",
"What is a way you stay motivated?",
"What is a habit that keeps you healthy?",
"What is something that makes you feel accomplished?",
"What is one thing you are grateful for right now?",
"What is a memory that brings you comfort?",
"What is something that encourages you daily?",
"What is a goal that excites you?"
]

# =============================
# QOTD QUESTIONS (251–500, fully mixed)
# =============================
QOTD_QUESTIONS += [
"What is a personal challenge you are proud of overcoming?",
"What is a moment you felt completely at peace?",
"What is one thing you want to improve in your daily routine?",
"What is something that inspires you to be better?",
"What is a skill you want to master this year?",
"What is a happy memory that makes you smile instantly?",
"What is something that makes you feel excited about life?",
"What is a way you practice self-care daily?",
"What is a goal you want to accomplish this week?",
"What is a lesson you learned from a mistake?",
"What is one thing that makes you feel confident?",
"What is a hobby that brings you joy and relaxation?",
"What is a memory that makes you laugh every time?",
"What is something that makes you feel inspired?",
"What is a decision you made that improved your life?",
"What is one thing you do to challenge yourself?",
"What is a dream you are actively pursuing?",
"What is a small habit that improves your day?",
"What is a quality you admire in others?",
"What is something that makes you feel motivated?",
"What is a skill that you want to develop further?",
"What is one thing that brings you peace of mind?",
"What is a favorite tradition you cherish?",
"What is a personal value that guides your actions?",
"What is something that helps you stay productive?",
"What is a goal that excites you for the future?",
"What is a way you express creativity?",
"What is something that makes you feel loved and appreciated?",
"What is a small act of kindness you recently did?",
"What is one thing you want to learn this month?",
"What is a habit that helps you stay balanced?",
"What is a memory that makes you feel grateful?",
"What is a topic you enjoy exploring deeply?",
"What is a dream destination you want to visit?",
"What is one thing you can do today to be happier?",
"What is something that inspires confidence in you?",
"What is a personal mantra you live by?",
"What is a moment that gave you pride?",
"What is a skill you recently improved?",
"What is a habit that makes you feel accomplished?",
"What is something that excites your curiosity?",
"What is one thing that motivates you every morning?",
"What is a lesson you learned from a challenging time?",
"What is a way you practice gratitude daily?",
"What is something that brings joy to your everyday life?",
"What is one thing you wish to accomplish this year?",
"What is a quality you want to strengthen in yourself?",
"What is a memory that brings you comfort when stressed?",
"What is a decision that changed your perspective positively?",
"What is something that helps you feel grounded?",
"What is one way you inspire others?",
"What is a dream you want to fulfill in the next five years?",
"What is something that gives you hope when things are tough?",
"What is a skill you admire in someone else and want to learn?",
"What is one thing that makes your day feel meaningful?",
"What is a memory that reminds you of your strength?",
"What is a goal you want to set for personal growth?",
"What is a habit that keeps you emotionally healthy?",
"What is something that makes you feel confident in social situations?",
"What is one thing that helps you stay creative?",
"What is a moment that made you feel completely happy?",
"What is a small success you are proud of recently?",
"What is a way you reflect on your personal progress?",
"What is something that inspires you to take action?",
"What is one thing you are grateful for in your life?",
"What is a challenge you want to overcome this year?",
"What is a memory that makes you feel loved?",
"What is a personal accomplishment that means a lot to you?",
"What is something that encourages you to grow?",
"What is a dream you hope to achieve soon?",
"What is a habit that keeps your mind sharp?",
"What is one thing that brings you peace daily?",
"What is a quality you respect in your friends?",
"What is something you enjoy doing to relax?",
"What is a moment that made you feel proud of someone else?",
"What is a skill that improves your life quality?",
"What is a personal goal you are excited about?",
"What is a memory that makes you smile with friends?",
"What is one thing you can do to improve your week?",
"What is a habit that helps you manage stress?",
"What is something that motivates you when you feel down?",
"What is a small goal you can achieve today?",
"What is a quality that makes someone inspiring to you?",
"What is one thing that makes your day better instantly?",
"What is a moment of kindness you remember vividly?",
"What is a challenge you faced that taught you resilience?",
"What is a memory that makes you laugh out loud?",
"What is something that brings excitement to your routine?",
"What is a skill you want to refine this year?",
"What is a way you express yourself creatively?",
"What is a memory you cherish with family?",
"What is one thing that keeps you grounded in life?",
"What is a personal lesson you learned from a friend?",
"What is something that makes you feel accomplished daily?",
"What is a goal you are planning to pursue next month?",
"What is a habit that keeps you motivated?",
"What is a moment that changed your outlook on life?",
"What is one thing that brings joy to your mornings?",
"What is a personal value you never compromise on?",
"What is a skill that makes you feel capable?",
"What is a habit that makes your evenings relaxing?",
"What is a memory that reminds you of your growth?",
"What is one thing that excites you about the future?",
"What is something you do to take care of your mental health?",
"What is a personal achievement that makes you proud?",
"What is a dream you are actively working towards?",
"What is a habit that improves your focus?",
"What is a memory that fills you with happiness?",
"What is a small act of kindness that you appreciate?",
"What is one thing that motivates your creativity?",
"What is a goal that inspires you this week?",
"What is a memory that reminds you of your potential?",
"What is something that gives you confidence in yourself?",
"What is a habit that keeps you energized daily?",
"What is a personal lesson you learned from a challenge?",
"What is a moment that gave you clarity?",
"What is a skill you want to practice more often?",
"What is a goal that makes you feel excited to wake up?",
"What is a memory that makes you feel thankful?",
"What is a habit that supports your emotional wellbeing?",
"What is a personal strength that helps you succeed?",
"What is one thing that brings laughter to your day?",
"What is a dream you hope to accomplish within a year?",
"What is a small accomplishment that makes you proud?",
"What is a memory that makes you feel peaceful?",
"What is a habit that boosts your confidence?",
"What is a skill that you use to help others?",
"What is a goal that pushes you to grow?",
"What is one thing that makes your evenings enjoyable?",
"What is a memory that reminds you of happy times?",
"What is a personal value that shapes your decisions?",
"What is something that helps you stay optimistic?",
"What is a goal you want to achieve by the end of this month?",
"What is a habit that you want to maintain consistently?",
"What is one thing that inspires you to improve daily?",
"What is a memory that motivates you when tired?",
"What is something that helps you stay resilient?",
"What is a small success you want to celebrate today?",
"What is a dream you want to fulfill in your lifetime?",
"What is one thing that brings joy unexpectedly?",
"What is a skill that makes you feel accomplished?",
"What is a habit that enhances your personal growth?",
"What is a memory that reminds you of your happiest moments?",
"What is a goal that excites you to take action?",
"What is a habit that strengthens your mind and body?",
"What is one thing that inspires creativity in you?",
"What is a memory that makes you feel grateful for life?",
"What is something that encourages you to face challenges?",
"What is a personal accomplishment that you cherish the most?",
"What is a goal that makes you proud of yourself?",
"What is one thing that makes your day more positive?",
"What is a skill that boosts your confidence?",
"What is a habit that helps you manage emotions?",
"What is a memory that makes you feel valued?",
"What is a goal that motivates you to be better?",
"What is one thing that brings you excitement this week?",
"What is a skill that inspires you to grow?",
"What is a memory that makes you feel loved and supported?",
"What is a habit that keeps you consistent?",
"What is a personal lesson you want to remember forever?",
"What is a small victory that makes you feel successful?",
"What is a goal that you are determined to achieve?",
"What is one thing that makes your mornings brighter?",
"What is a skill that makes your daily life easier?",
"What is a habit that improves your mental clarity?",
"What is a memory that makes you smile randomly?",
"What is a goal that gives you purpose today?",
"What is a personal value that guides your actions consistently?",
"What is one thing that inspires hope in you?"
]

# =============================
# EMBED CONFIG
# =============================
def get_embed_config():
    c.execute("SELECT * FROM qotd_embed WHERE id=1")
    row = c.fetchone()
    if not row:
        c.execute("""
        INSERT INTO qotd_embed VALUES
        (1, '🌅 **Question of the Day**', 'QOTD', '{question}',
         'Daily QOTD', NULL, NULL, NULL, 0x5865F2)
        """)
        conn.commit()
        return get_embed_config()
    return row

# =============================
# SEND QOTD
# =============================
async def send_qotd():
    c.execute("SELECT current_index FROM qotd_state WHERE id=1")
    idx = c.fetchone()[0]

    if idx >= len(QOTD_QUESTIONS):
        return

    question = QOTD_QUESTIONS[idx]
    config = get_embed_config()

    channel = bot.get_channel(QOTD_CHANNEL_ID)
    if not channel:
        return

    embed = nextcord.Embed(
        title=config[2],
        description=config[3].replace("{question}", question),
        color=config[8]
    )

    if config[6]:
        embed.set_image(url=config[6])
    if config[7]:
        embed.set_thumbnail(url=config[7])
    if config[4]:
        embed.set_footer(text=config[4], icon_url=config[5])

    msg = await channel.send(
        content=f"<@&{QOTD_ROLE_ID}>\n{config[1]}",
        embed=embed
    )

    await msg.create_thread(name=f"QOTD #{idx+1}")
    c.execute("UPDATE qotd_state SET current_index=?", (idx+1,))
    conn.commit()

# =============================
# SCHEDULER
# =============================
@tasks.loop(minutes=1)
async def qotd_scheduler():
    now = datetime.now(IST)
    if now.hour == 7 and now.minute == 30:
        await send_qotd()
        await nextcord.utils.sleep_until(
            datetime.combine(now.date() + timedelta(days=1), time(7, 30, tzinfo=IST))
        )

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not qotd_scheduler.is_running():
        qotd_scheduler.start()

# =============================
# SLASH COMMANDS
# =============================
@bot.slash_command(description="Customise QOTD embed (Admin only)")
async def customise_qotd_embed(
    interaction: Interaction,
    line: str = SlashOption(required=False),
    title: str = SlashOption(required=False),
    description: str = SlashOption(required=False),
    footer: str = SlashOption(required=False),
    footer_icon: str = SlashOption(required=False),
    image: str = SlashOption(required=False),
    thumbnail: str = SlashOption(required=False),
    color: str = SlashOption(required=False),
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Admins only", ephemeral=True)
        return

    current = get_embed_config()
    c.execute("""
    UPDATE qotd_embed SET
    line=?, title=?, description=?, footer=?, footer_icon=?,
    image=?, thumbnail=?, color=? WHERE id=1
    """, (
        line or current[1],
        title or current[2],
        description or current[3],
        footer or current[4],
        footer_icon or current[5],
        image or current[6],
        thumbnail or current[7],
        int(color, 16) if color else current[8]
    ))
    conn.commit()
    await interaction.response.send_message("QOTD embed updated")

@bot.slash_command(description="Test QOTD embed")
async def test_qotd_embed(interaction: Interaction):
    config = get_embed_config()
    embed = nextcord.Embed(
        title=config[2],
        description=config[3].replace("{question}", "This is a test question"),
        color=config[8]
    )
    await interaction.response.send_message(config[1], embed=embed, ephemeral=True)

# =============================
# RUN BOT
# =============================
bot.run(BOT_TOKEN)
