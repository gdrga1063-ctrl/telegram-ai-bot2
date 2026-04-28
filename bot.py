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

# --- ЛОГИ ---
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

# Railway сам даёт PORT
PORT = int(os.environ.get("PORT", 8000))

# --- ОБРАБОТЧИКИ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я здесь.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print("Сообщение:", text)

    reply = f"Ты сказал: {text}"
    await update.message.reply_text(reply)

# --- ЗАПУСК ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ВАЖНО: Railway URL
    WEBHOOK_URL = os.getenv("RAILWAY_STATIC_URL")

    if not WEBHOOK_URL:
        print("❌ Нет RAILWAY_STATIC_URL")
        return

    WEBHOOK_URL = f"https://{WEBHOOK_URL}"

    print("Webhook:", WEBHOOK_URL)

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
