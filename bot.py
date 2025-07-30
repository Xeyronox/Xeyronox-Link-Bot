import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Initialize Telegram bot
application = Application.builder().token(BOT_TOKEN).build()

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📷 Instagram", url="https://instagram.com/xeyronox")],
        [InlineKeyboardButton("💻 GitHub", url="https://github.com/Xeyronox")],
        [InlineKeyboardButton("📢 Telegram Channel", url="https://t.me/Xeyronox1")],
        [InlineKeyboardButton("👤 Telegram Profile", url="https://t.me/Xeyronox")],
        [InlineKeyboardButton("🛒 Tool Shop", url="https://xeyronox-shop.vercel.app")],
        [InlineKeyboardButton("📺 YouTube", url="https://www.youtube.com/@Xeyronox")],
    ]
    await update.message.reply_text(
        "👋 Welcome to *Xeyronox Link Bot!*\n\nHere are my official links 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ *Available Commands:*\n\n"
        "/start - Show official links\n"
        "/help - Show this help message\n"
        "/shop - Visit hacking tools shop\n"
        "/portfolio - View portfolio (coming soon)\n\n"
        "💡 Some tools are available free at our [GitHub](https://github.com/Xeyronox)."
    )
    await update.message.reply_markdown(text)

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🛍️ Open Tool Shop", url="https://xeyronox-shop.vercel.app")]]
    await update.message.reply_text("🧰 Check out my hacking tools:", reply_markup=InlineKeyboardMarkup(keyboard))

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔧 Portfolio coming soon!", callback_data="coming_soon")]]
    await update.message.reply_text("🚧 Portfolio is under construction.", reply_markup=InlineKeyboardMarkup(keyboard))

# Health check route (for Render)
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

# Telegram Webhook Route
@app.post("/XeyronoxLinkBot")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# Main setup
async def setup():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("shop", shop))
    application.add_handler(CommandHandler("portfolio", portfolio))

    await application.bot.set_webhook(WEBHOOK_URL)

import asyncio
asyncio.run(setup())