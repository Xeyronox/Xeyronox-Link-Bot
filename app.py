
import os
import time
import random
import logging
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app for webhook
app = Flask(__name__)

# Bot configuration
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://xeyronox-link-bot-n9pl.onrender.com')

# Global application variable
telegram_app = None

# Hacker quotes for daily messages
HACKER_QUOTES = [
    "ðŸ’€ The best way to predict the future is to create it - developed by Xeyronox || Red/Black Hat Hacker",
    "ðŸ”´ In the world of zeros and ones, we are the exceptions - developed by Xeyronox || Red/Black Hat Hacker", 
    "âš« Security is not a product, but a process - developed by Xeyronox || Red/Black Hat Hacker",
    "ðŸ’» Think like a hacker, defend like a guardian - developed by Xeyronox || Red/Black Hat Hacker",
    "ðŸŽ¯ The only system which is truly secure is one which is switched off - developed by Xeyronox || Red/Black Hat Hacker",
    "ðŸ” Hacking is not about breaking things, it's about understanding them - developed by Xeyronox || Red/Black Hat Hacker",
    "âš¡ Code is poetry written in logic - developed by Xeyronox || Red/Black Hat Hacker",
    "ðŸš€ Every system has vulnerabilities, every problem has solutions - developed by Xeyronox || Red/Black Hat Hacker"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("ðŸ“· Instagram", url="https://instagram.com/xeyronox"),
            InlineKeyboardButton("ðŸ’» GitHub", url="https://github.com/Xeyronox")
        ],
        [
            InlineKeyboardButton("ðŸ“¢ Channel", url="https://t.me/Xeyronox1"),
            InlineKeyboardButton("ðŸ‘¤ Profile", url="https://t.me/Xeyronox")
        ],
        [
            InlineKeyboardButton("ðŸ›’ Shop", url="https://xeyronox-shop.vercel.app"),
            InlineKeyboardButton("ðŸ“º YouTube", url="https://www.youtube.com/@Xeyronox")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = """ðŸ”¥ **Welcome to Xeyronox Link Bot!** ðŸ”¥

ðŸŽ¯ Your gateway to the cyber world of Xeyronox
ðŸ”´âš« Red/Black Hat Hacker Tools & Resources

Select any option below to explore:

ðŸ’¡ **Daily Hack Tip:** """ + random.choice(HACKER_QUOTES)

    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help instructions."""
    help_text = """ðŸ¤– **Xeyronox Link Bot - Help Menu**

**Available Commands:**
â€¢ `/start` - Welcome message with main links
â€¢ `/help` - Show this help menu  
â€¢ `/links` - Display all official links
â€¢ `/shop` - Direct link to hacking tool shop
â€¢ `/portfolio` - Portfolio section (coming soon)
â€¢ `/language` - Language selection (English only currently)

**Features:**
ðŸ”— Quick access to all Xeyronox social media
ðŸ›’ Direct shop access for hacking tools
ðŸ“± User-friendly interface with inline buttons
ðŸ”„ Regular updates with new features

**Developer:** Xeyronox || Red/Black Hat Hacker
**Version:** 1.0.0

For support, visit: https://t.me/Xeyronox"""

    await update.message.reply_text(help_text, parse_mode='Markdown')

async def links_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display all official links."""
    keyboard = [
        [
            InlineKeyboardButton("ðŸ“· Instagram", url="https://instagram.com/xeyronox"),
            InlineKeyboardButton("ðŸ’» GitHub", url="https://github.com/Xeyronox")
        ],
        [
            InlineKeyboardButton("ðŸ“¢ Channel", url="https://t.me/Xeyronox1"),
            InlineKeyboardButton("ðŸ‘¤ Profile", url="https://t.me/Xeyronox")
        ],
        [
            InlineKeyboardButton("ðŸ›’ Shop", url="https://xeyronox-shop.vercel.app"),
            InlineKeyboardButton("ðŸ“º YouTube", url="https://www.youtube.com/@Xeyronox")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    links_message = """ðŸ”— **Official Xeyronox Links**

ðŸŒ **Social Media & Platforms:**
â€¢ Instagram: Professional updates & content
â€¢ GitHub: Open source projects & code
â€¢ Telegram Channel: Latest announcements  
â€¢ Telegram Profile: Direct contact
â€¢ YouTube: Video tutorials & demos

ðŸ›’ **Shop:** Premium hacking tools & resources

**Developer:** Xeyronox || Red/Black Hat Hacker"""

    await update.message.reply_text(
        links_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Direct link to hacking tool shop."""
    keyboard = [
        [InlineKeyboardButton("ðŸ›’ Visit Shop", url="https://xeyronox-shop.vercel.app")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    shop_message = """ðŸ›’ **Xeyronox Hacking Tool Shop**

ðŸ’» **Premium Tools Available:**
â€¢ Penetration Testing Utilities
â€¢ Network Security Tools  
â€¢ Vulnerability Scanners
â€¢ Custom Scripts & Exploits
â€¢ Educational Resources

ðŸ” **Quality Guaranteed**
âš¡ **Instant Access**
ðŸŽ¯ **Professional Grade Tools**

**Developer:** Xeyronox || Red/Black Hat Hacker"""

    await update.message.reply_text(
        shop_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Portfolio section - coming soon."""
    keyboard = [
        [InlineKeyboardButton("ðŸ“¢ Get Notified", url="https://t.me/Xeyronox1")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    portfolio_message = """ðŸ“ **Portfolio Section**

ðŸš§ **Coming Soon!** ðŸš§

This section will feature:
â€¢ Completed projects showcase
â€¢ Client testimonials  
â€¢ Case studies
â€¢ Achievement gallery
â€¢ Technical demonstrations

ðŸ“¢ **Stay Updated:** Join our channel to get notified when this feature launches!

**Developer:** Xeyronox || Red/Black Hat Hacker"""

    await update.message.reply_text(
        portfolio_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Language selection - currently English only."""
    keyboard = [
        [InlineKeyboardButton("ðŸ‡ºðŸ‡¸ English (Current)", callback_data="lang_en")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    language_message = """ðŸŒ **Language Selection**

**Currently Available:**
ðŸ‡ºðŸ‡¸ English (Active)

**Coming Soon:**
ðŸ‡ªðŸ‡¸ Spanish
ðŸ‡«ðŸ‡· French  
ðŸ‡©ðŸ‡ª German
ðŸ‡·ðŸ‡º Russian

More languages will be added based on user demand.

**Developer:** Xeyronox || Red/Black Hat Hacker"""

    await update.message.reply_text(
        language_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data == "lang_en":
        await query.edit_message_text(
            "âœ… **English is already selected!**\n\nYou're using the default language.",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown messages gracefully."""
    keyboard = [
        [InlineKeyboardButton("ðŸ†˜ Get Help", callback_data="help")],
        [InlineKeyboardButton("ðŸ  Main Menu", callback_data="start")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    unknown_message = """â“ **Unknown Command**

I didn't understand that message. Here's what I can help you with:

**Available Commands:**
â€¢ `/start` - Main menu
â€¢ `/help` - Help instructions  
â€¢ `/links` - All official links
â€¢ `/shop` - Hacking tool shop
â€¢ `/portfolio` - Portfolio (coming soon)
â€¢ `/language` - Language selection

**Developer:** Xeyronox || Red/Black Hat Hacker"""

    await update.message.reply_text(
        unknown_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def send_daily_hacker_message():
    """Send daily hacker style message (to be called by scheduler)."""
    quote = random.choice(HACKER_QUOTES)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    daily_message = f"""ðŸ”¥ **Daily Hacker Wisdom** ðŸ”¥

{quote}

â° **Time:** {current_time}
ðŸŽ¯ **Stay Sharp, Stay Secure!**"""

    return daily_message

def create_application():
    """Create and configure the Telegram application."""
    global telegram_app

    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    # Create application
    telegram_app = Application.builder().token(TOKEN).build()

    # Register handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("help", help_command))
    telegram_app.add_handler(CommandHandler("links", links_command))
    telegram_app.add_handler(CommandHandler("shop", shop_command))
    telegram_app.add_handler(CommandHandler("portfolio", portfolio_command))
    telegram_app.add_handler(CommandHandler("language", language_command))
    telegram_app.add_handler(CallbackQueryHandler(button_callback))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return telegram_app

# Health check endpoint for Render
@app.route('/health')
def health_check(): 
    """Health check endpoint for monitoring."""
    try:
        bot_status = "healthy" if telegram_app else "not_initialized"
        return jsonify({
            'status': 'healthy',
            'bot': 'Xeyronox Link Bot',
            'bot_status': bot_status,
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'developer': 'Xeyronox || Red/Black Hat Hacker',
            'daily_quote': random.choice(HACKER_QUOTES)
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhooks from Telegram."""
    try:
        if not telegram_app:
            logger.error("Telegram application not initialized")
            return jsonify({'error': 'Bot not initialized'}), 500

        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, telegram_app.bot)

        # Process the update asynchronously
        asyncio.create_task(telegram_app.process_update(update))

        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500

# Root route
@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        'bot': 'Xeyronox Link Bot',
        'status': 'running',
        'developer': 'Xeyronox || Red/Black Hat Hacker',
        'version': '1.0.0',
        'health_endpoint': '/health',
        'webhook_endpoint': '/webhook',
        'daily_wisdom': random.choice(HACKER_QUOTES)
    })

async def set_webhook():
    """Set the webhook URL."""
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        await telegram_app.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return False

async def initialize_bot():
    """Initialize the bot and set webhook."""
    try:
        # Create application
        create_application()

        # Initialize the bot
        await telegram_app.initialize()

        # Set webhook
        await set_webhook()

        logger.info("Bot initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        return False

# Initialize everything when the module is loaded
if __name__ == '__main__':
    # Run initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        success = loop.run_until_complete(initialize_bot())
        if not success:
            logger.error("Bot initialization failed")
    except Exception as e:
        logger.error(f"Initialization error: {e}")

    # Start the Flask app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # When run by gunicorn, initialize the bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(initialize_bot())
    except Exception as e:
        logger.error(f"Gunicorn initialization error: {e}")
