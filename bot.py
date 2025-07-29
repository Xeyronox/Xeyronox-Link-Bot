import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from telegram.ext.fastapi import create_application

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# FastAPI instance for webhook + /healthz
fastapi_app = FastAPI()


# ========== Telegram Command Handlers ==========

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


# ========== FastAPI Health Check Endpoint ==========

@fastapi_app.get("/healthz")
async def health_check():
    return {"status": "ok"}


# ========== Main Async Entrypoint ==========

async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("shop", shop))
    application.add_handler(CommandHandler("portfolio", portfolio))

    # Set Telegram webhook
    await application.bot.set_webhook(url=WEBHOOK_URL)

    # Mount FastAPI app for Telegram webhook
    telegram_app = create_application(application)
    fastapi_app.mount("/", telegram_app)


# Run
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())