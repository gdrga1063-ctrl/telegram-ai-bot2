import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("8207302663:AAG46mdKUzQnpEaCVbDbTDgzpijO6sX3rno")
PORT = int(os.environ.get("PORT", 8000))
WEBHOOK_URL = os.getenv("RAILWAY_STATIC_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я здесь.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print("Сообщение:", text)
    await update.message.reply_text(f"Ты сказал: {text}")

def main():
    print("=== СТАРТ БОТА ===")

    if not TOKEN:
        print("❌ Нет BOT_TOKEN")
        return

    if not WEBHOOK_URL:
        print("❌ Нет RAILWAY_STATIC_URL")
        return

    WEBHOOK_URL_FULL = f"https://{WEBHOOK_URL}"
    print("Webhook URL:", WEBHOOK_URL_FULL)
    print("Port:", PORT)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL_FULL,
    )

if __name__ == "__main__":
    main()
