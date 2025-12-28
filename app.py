import os
import json
import requests
import asyncio
import mysql.connector
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# -----------------------------
# 🔧 Load environment variables
# -----------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_REG_SECRET = os.getenv("ADMIN_REG_SECRET", "changeme")

ADMINS_FILE = Path("admins.json")
if not ADMINS_FILE.exists():
    ADMINS_FILE.write_text(json.dumps([]))

# -----------------------------
# 🗄️ Database Connection (MySQL)
# -----------------------------
try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",  # change if you set a MySQL password
        database="telegram_dashboard"
    )
    cursor = db.cursor()
    print("✅ Database connected successfully.")
except Exception as e:
    print("❌ Database connection failed:", e)

# -----------------------------
# 🔐 Admin Management
# -----------------------------
def load_admins():
    return json.loads(ADMINS_FILE.read_text())

def save_admins(admins):
    ADMINS_FILE.write_text(json.dumps(admins, indent=2))

# -----------------------------
# 🤖 Bot Commands
# -----------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👮 Police Security Bot active.\n"
        "If you are an admin, register with:\n"
        "/register_admin <secret>\n\n"
        "Public users: Send any message — suspicious ones will be reviewed by admins."
    )

async def register_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat_id = update.effective_chat.id
    if len(args) < 1:
        await update.message.reply_text("Usage: /register_admin <secret>")
        return

    secret = args[0]
    if secret != ADMIN_REG_SECRET:
        await update.message.reply_text("❌ Invalid secret.")
        return

    admins = load_admins()
    if chat_id in admins:
        await update.message.reply_text("You are already registered as admin.")
        return

    admins.append(chat_id)
    save_admins(admins)
    await update.message.reply_text("✅ Registration successful. You will now receive suspicious alerts.")

async def unregister_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    admins = load_admins()
    if chat_id not in admins:
        await update.message.reply_text("You are not registered as admin.")
        return
    admins.remove(chat_id)
    save_admins(admins)
    await update.message.reply_text("You have been removed from admin list.")

async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = load_admins()
    await update.message.reply_text(f"Registered Admin IDs:\n{admins}")

# -----------------------------
# 🧠 AI Classification (OpenRouter)
# -----------------------------
def classify_message_with_openrouter(text: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-bot-name.example",
        "X-Title": "Police Security Bot",
    }

    prompt = [
        {
            "role": "system",
            "content": (
                "You are a security AI that classifies Telegram messages as 'safe' or 'suspicious'.\n"
                "Mark as 'suspicious' if it contains scams, illegal trade, hacking, terrorism, drugs, or threats.\n"
                "Reply ONLY in JSON format like:\n"
                '{"label":"suspicious","score":0.9,"reasons":["scam","fraudulent"]}'
            ),
        },
        {"role": "user", "content": f"Message: {text}"},
    ]

    payload = {
        "model": "gpt-4o-mini",
        "messages": prompt,
        "max_tokens": 150,
        "temperature": 0.0,
    }

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        return json.loads(raw)
    except Exception as e:
        print("⚠️ AI fallback triggered:", e)
        lower = text.lower()
        keywords = ["hack", "scam", "illegal", "weapon", "drugs", "kill", "terror"]
        label = "suspicious" if any(k in lower for k in keywords) else "safe"
        return {
            "label": label,
            "score": 0.9 if label == "suspicious" else 0.1,
            "reasons": ["keyword_fallback"]
        }

# -----------------------------
# 📩 Handle Messages
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = msg.text or ""
    chat_id = msg.chat.id
    sender_name = msg.from_user.username or msg.from_user.first_name or str(msg.from_user.id)

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception as e:
        print("⚠️ Telegram action error:", e)

    # 🧠 Classify message
    result = classify_message_with_openrouter(text)
    label = result.get("label", "safe")
    score = float(result.get("score", 0.0))
    reasons = json.dumps(result.get("reasons", []))

    # 💾 Save message including AI classification
    try:
        sql = """
        INSERT INTO messages (chat_id, username, text, created_at, label, score, reasons)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            chat_id,
            sender_name,
            text,
            datetime.now(),
            label,
            round(score, 2),
            reasons
        )
        cursor.execute(sql, values)
        db.commit()
        print(f"💾 Saved message from @{sender_name} (label={label}, score={score})")
    except Exception as e:
        print("❌ DB Insert Error:", e)

    # ✅ Reply to user
    try:
        if label == "suspicious" and score >= 0.5:
            await msg.reply_text(
                "⚠️ This message seems *suspicious*. Our security team will review it.",
                parse_mode="Markdown",
            )
        else:
            await msg.reply_text("✅ Message received safely.")
    except Exception as e:
        print("⚠️ Telegram reply error:", e)

    # 🚨 Notify Admins
    if label == "suspicious" and score >= 0.5:
        admins = load_admins()
        if admins:
            alert = (
                f"🚨 *Suspicious Message Detected!*\n"
                f"*User:* {sender_name}\n"
                f"*Chat ID:* `{chat_id}`\n"
                f"*Message:* {text}\n"
                f"*Score:* {score}\n"
                f"*Reasons:* {reasons}"
            )
            for a in admins:
                try:
                    await context.bot.send_message(a, alert, parse_mode="Markdown")
                except Exception as e:
                    print(f"⚠️ Failed to alert admin {a}: {e}")

# -----------------------------
# 🚀 Run the Bot
# -----------------------------
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN missing in .env")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("register_admin", register_admin))
    app.add_handler(CommandHandler("unregister_admin", unregister_admin))
    app.add_handler(CommandHandler("list_admins", list_admins))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot started. Listening for messages...")
    try:
        asyncio.run(app.run_polling(allowed_updates=Update.ALL_TYPES))
    except Exception as e:
        print("❌ Error running bot:", e)
