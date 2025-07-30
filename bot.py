import os
import logging
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any
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
)
import asyncio
import uvicorn
import json
from pathlib import Path

# Load environment variables with fallback values
load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", "10000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN or not cls.WEBHOOK_URL:
            raise ValueError("BOT_TOKEN and WEBHOOK_URL must be set in .env file")

# Validate configuration
Config.validate()

# Setup logging with rotation
log_file = Path("logs/bot.log")
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI with enhanced error handling
app = FastAPI(
    title="Xeyronox Link Bot",
    version="2.1.0",
    docs_url="/docs" if Config.DEBUG else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced error handling
class BotError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

@app.exception_handler(BotError)
async def bot_exception_handler(request: Request, exc: BotError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# Initialize bot with retry mechanism
class RetryableApplication:
    def __init__(self, token: str, max_retries: int = 3):
        self.token = token
        self.max_retries = max_retries
        self.application = None

    async def initialize(self):
        for attempt in range(self.max_retries):
            try:
                self.application = Application.builder().token(self.token).build()
                return self.application
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise BotError(f"Failed to initialize bot after {self.max_retries} attempts: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

bot_app = RetryableApplication(Config.BOT_TOKEN, Config.RETRY_ATTEMPTS)

# Command handlers with automatic retry
async def with_retry(func, *args, **kwargs):
    for attempt in range(Config.RETRY_ATTEMPTS):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == Config.RETRY_ATTEMPTS - 1:
                raise
            logger.warning(f"Retry attempt {attempt + 1} for {func.__name__}: {e}")
            await asyncio.sleep(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📷 Instagram", url="https://instagram.com/xeyronox")],
        [InlineKeyboardButton("💻 GitHub", url="https://github.com/Xeyronox")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/Xeyronox1")],
        [InlineKeyboardButton("👤 Profile", url="https://t.me/Xeyronox")],
        [InlineKeyboardButton("🛒 Shop", url="https://xeyronox-shop.vercel.app")],
        [InlineKeyboardButton("📺 YouTube", url="https://www.youtube.com/@Xeyronox")],
    ]
    await with_retry(
        update.message.reply_text,
        "👋 Welcome to *Xeyronox Link Bot!*\n\nHere are my official links 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_info = {
        "time_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "environment": Config.ENVIRONMENT,
        "uptime": time.time() - bot_start_time,
        "version": "2.1.0"
    }
    
    status_text = (
        f"🤖 *Bot Status*\n\n"
        f"🕒 UTC: {status_info['time_utc']}\n"
        f"⚙️ Env: {status_info['environment']}\n"
        f"⏱️ Uptime: {int(status_info['uptime'])}s\n"
        f"📦 Version: {status_info['version']}"
    )
    
    await with_retry(
        update.message.reply_text,
        status_text,
        parse_mode="Markdown"
    )

# Health check endpoint
@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": Config.ENVIRONMENT,
        "uptime": time.time() - bot_start_time
    }

# Webhook handler
@app.post(f"/{Config.BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot_app.application.bot)
        await bot_app.application.process_update(update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"ok": False, "error": str(e)}
        )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    global bot_start_time
    bot_start_time = time.time()
    
    # Initialize bot
    application = await bot_app.initialize()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    
    # Set webhook
    webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Bot started successfully. Webhook set to {webhook_url}")

@app.on_event("shutdown")
async def shutdown_event():
    if bot_app.application:
        await bot_app.application.shutdown()
    logger.info("Bot shutdown completed")

# Main execution
if __name__ == "__main__":
    try:
        uvicorn.run(
            "bot:app",
            host="0.0.0.0",
            port=Config.PORT,
            reload=Config.DEBUG,
            log_level="debug" if Config.DEBUG else "info",
            workers=1
        )
    except Exception as e:
        logger.critical(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)