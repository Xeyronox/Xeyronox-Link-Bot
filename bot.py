import os
import logging
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status, HTTPException
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
import asyncio
import uvicorn
from pythonjsonlogger import jsonlogger

# Load and validate environment variables
load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", "10000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))
    ALLOWED_UPDATES = os.getenv("ALLOWED_UPDATES", '["message", "callback_query"]')
    START_TIME = datetime.utcnow()

    @classmethod
    def validate(cls):
        required = ["BOT_TOKEN", "WEBHOOK_URL"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Validate configuration
Config.validate()

# Setup enhanced logging
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['environment'] = Config.ENVIRONMENT

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "bot.log"

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, Config.LOG_LEVEL))

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(CustomJsonFormatter())
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(CustomJsonFormatter())
logger.addHandler(file_handler)

# Initialize FastAPI with enhanced middleware
app = FastAPI(
    title="Xeyronox Link Bot",
    version="2.2.0",
    docs_url="/docs" if Config.DEBUG else None,
    redoc_url="/redoc" if Config.DEBUG else None
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handling
class BotException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

@app.exception_handler(BotException)
async def bot_exception_handler(request: Request, exc: BotException):
    logger.error(f"Bot error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )

# Initialize bot with retry mechanism
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def initialize_bot() -> Application:
    application = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .rate_limiter(AIORateLimiter(max_retries=Config.MAX_RETRIES))
        .build()
    )
    return application

# Command handlers with automatic retry
class CommandHandlers:
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📷 Instagram", url="https://instagram.com/xeyronox")],
            [InlineKeyboardButton("💻 GitHub", url="https://github.com/Xeyronox")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/Xeyronox1")],
            [InlineKeyboardButton("👤 Profile", url="https://t.me/Xeyronox")],
            [InlineKeyboardButton("🛒 Shop", url="https://xeyronox-shop.vercel.app")],
            [InlineKeyboardButton("📺 YouTube", url="https://www.youtube.com/@Xeyronox")]
        ]
        await update.message.reply_text(
            "👋 Welcome to *Xeyronox Link Bot!*\n\nHere are my official links 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = datetime.utcnow() - Config.START_TIME
        status_text = (
            f"🤖 *Bot Status Report*\n\n"
            f"🕒 Current Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"⚙️ Environment: {Config.ENVIRONMENT}\n"
            f"⏱️ Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m\n"
            f"📦 Version: 2.2.0\n"
            f"🔄 Last Updated: 2024-02-13"
        )
        await update.message.reply_text(status_text, parse_mode="Markdown")

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "*Available Commands:*\n\n"
            "/start - Show all social links\n"
            "/status - Check bot status\n"
            "/help - Show this help message"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

# Health check endpoint with enhanced monitoring
@app.get("/healthz")
async def healthz():
    uptime = datetime.utcnow() - Config.START_TIME
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": Config.ENVIRONMENT,
        "version": "2.2.0",
        "uptime_seconds": uptime.total_seconds(),
        "memory_usage": sys.getsizeof(sys.modules),
    }

# Webhook handler with enhanced error handling
@app.post(f"/{Config.BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        raise BotException(message="Failed to process webhook update", status_code=500)

# Application state
application: Optional[Application] = None

# Startup event
@app.on_event("startup")
async def startup_event():
    global application
    try:
        # Initialize bot
        application = await initialize_bot()
        
        # Register handlers
        application.add_handler(CommandHandler("start", CommandHandlers.start))
        application.add_handler(CommandHandler("status", CommandHandlers.status))
        application.add_handler(CommandHandler("help", CommandHandlers.help))
        
        # Set webhook
        webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
        await application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=eval(Config.ALLOWED_UPDATES),
            drop_pending_updates=True
        )
        
        logger.info(f"Bot started successfully. Webhook set to {webhook_url}")
        
        # Verify bot connection
        me = await application.bot.get_me()
        logger.info(f"Bot information - ID: {me.id}, Username: @{me.username}")
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}", exc_info=True)
        raise BotException(message="Failed to initialize bot", status_code=500)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    global application
    if application:
        await application.shutdown()
        logger.info("Bot shutdown completed successfully")

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
        logger.critical(f"Failed to start server: {str(e)}", exc_info=True)
        sys.exit(1)