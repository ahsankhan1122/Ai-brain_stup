import asyncio
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import threading

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Telegram Bot Token
TOKEN = "token"
CHAT_ID = "id"

# Sample /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("System is running. Use /signal to get the signal.")

# Sample /signal command
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Signal logic goes here.")

# Initialization and run logic
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))

    # Notify admin that bot is live
    await app.bot.send_message(chat_id=CHAT_ID, text="✅ AI Crypto System is ONLINE.")

    await app.run_polling()

def run_async_bot():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except RuntimeError as e:
        logging.error(f"RuntimeError in Telegram bot: {e}")

# Run bot in a separate thread
def start_bot():
    thread = threading.Thread(target=run_async_bot, daemon=True)
    thread.start()

if __name__ == "__main__":
    start_bot()
