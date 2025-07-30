import os
import logging
import sys
from datetime import datetime
from typing import Optional, Any
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    AIORateLimiter,
)
from telegram.error import TelegramError
import asyncio
import uvicorn

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN and WEBHOOK_URL must be set in .env file")

# Enhanced Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI with CORS and error handling
app = FastAPI(title="Xeyronox Link Bot", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# Initialize Telegram bot with rate limiting
application = (
    Application.builder()
    .token(BOT_TOKEN)
    .rate_limiter(AIORateLimiter(max_retries=3))
    .build()
)

# Utility function for error handling
async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    error_message = "An error occurred while processing your request. Please try again later."
    
    if update and update.effective_message:
        await update.effective_message.reply_text(error_message)

# Command Handlers with error handling
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
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
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        await error_handler(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = (
            "ℹ️ *Available Commands:*\n\n"
            "/start - Show official links\n"
            "/help - Show this help message\n"
            "/shop - Visit hacking tools shop\n"
            "/portfolio - View portfolio\n"
            "/status - Check bot status\n\n"
            "💡 Some tools are available free at our [GitHub](https://github.com/Xeyronox)."
        )
        await update.message.reply_markdown(text)
    except Exception as e:
        logger.error(f"Error in help command: {e}", exc_info=True)
        await error_handler(update, context)

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        keyboard = [[InlineKeyboardButton("🛍️ Open Tool Shop", url="https://xeyronox-shop.vercel.app")]]
        await update.message.reply_text(
            "🧰 Check out my hacking tools:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Error in shop command: {e}", exc_info=True)
        await error_handler(update, context)

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        keyboard = [[InlineKeyboardButton("🔧 View Portfolio", url="https://xeyronox.com")]]
        await update.message.reply_text(
            "📂 Check out my portfolio!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Error in portfolio command: {e}", exc_info=True)
        await error_handler(update, context)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        status_text = (
            "🤖 *Bot Status*\n\n"
            f"🕒 Current UTC Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🌐 Environment: {ENVIRONMENT}\n"
            "✅ Bot is running normally"
        )
        await update.message.reply_markdown(status_text)
    except Exception as e:
        logger.error(f"Error in status command: {e}", exc_info=True)
        await error_handler(update, context)

# Callback Query Handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()
    except Exception as e:
        logger.error(f"Error in button callback: {e}", exc_info=True)
        await error_handler(update, context)

# Health check route
@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": ENVIRONMENT
    }

# Telegram Webhook Route
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"ok": False, "error": str(e)}
        )

# Setup function
async def setup():
    try:
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("shop", shop))
        application.add_handler(CommandHandler("portfolio", portfolio))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Register error handler
        application.add_error_handler(error_handler)

        # Set webhook
        webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
        
        # Test bot connection
        me = await application.bot.get_me()
        logger.info(f"Bot started successfully. Bot username: @{me.username}")
    
    except Exception as e:
        logger.critical(f"Failed to setup bot: {e}", exc_info=True)
        sys.exit(1)

# Main execution
if __name__ == "__main__":
    # Setup the application
    asyncio.run(setup())
    
    # Run the FastAPI application
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info",
        workers=1
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())