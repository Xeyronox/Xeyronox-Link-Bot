import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_URL")  # e.g. https://yourrenderapp.onrender.com

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

LINKS = {
    "Instagram": "https://instagram.com/xeyronox",
    "GitHub (Some tools are free!)": "https://github.com/Xeyronox",
    "Telegram (Personal)": "https://t.me/Xeyronox",
    "Telegram Channel": "https://t.me/Xeyronox1",
    "YouTube": "https://www.youtube.com/@Xeyronox",
    "🛒 Tool Shop": "https://xeyronox-shop.vercel.app",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to Xeyronox's Link Bot!\n\n"
        "Use /links to see my official profiles and tool shop.\n"
        "Use /help to learn more about this bot."
    )
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 Help Menu\n\n"
        "/start – Welcome message\n"
        "/links – Get my official account and shop links\n"
        "/shop – View tool shop\n"
        "/portfolio – View upcoming portfolio\n"
        "/language – Choose language (English only currently)\n"
        "/help – Show this help message\n\n"
        "💡 Note: Some tools are available for free on my GitHub!"
    )
    await update.message.reply_text(help_text)


async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, url=url)] for name, url in LINKS.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔗 Click a link below:", reply_markup=reply_markup)


async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🛒 Visit Tool Shop", url=LINKS["🛒 Tool Shop"])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Here’s the shop for hacking tools:", reply_markup=reply_markup)


async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📁 Coming Soon", callback_data="coming_soon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("My portfolio will be live soon:", reply_markup=reply_markup)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🇺🇸 English (Only language supported)", callback_data="lang_en")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌐 Please select your language:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "coming_soon":
        await query.answer("This feature is coming soon! Stay tuned.", show_alert=True)
    elif query.data == "lang_en":
        await query.edit_message_text("Language set to English. (Only English supported currently)")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command. Try /help for a list of commands.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required in .env")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("links", links))
    app.add_handler(CommandHandler("shop", shop_command))
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_error_handler(error_handler)

    # Fetch bot username from Telegram
    bot_user = await app.bot.get_me()
    bot_username = bot_user.username
    logger.info(f"Bot username detected: @{bot_username}")

    if WEBHOOK_BASE_URL:
        webhook_path = f"/{bot_username}"
        webhook_url = WEBHOOK_BASE_URL.rstrip("/") + webhook_path

        logger.info(f"Starting webhook with URL: {webhook_url}")

        # PORT for render or default 8443
        port = int(os.environ.get("PORT", 8443))

        await app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=bot_username,
            webhook_url=webhook_url,
        )
    else:
        logger.info("No WEBHOOK_URL found, running in polling mode.")
        await app.run_polling()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())