import logging
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CommandHandler,
    filters,
)

from main import ai_generate, state, remember, update_state, dialog_memory

# --- ТОКЕН ---
TOKEN = os.getenv("8207302663:AAG46mdKUzQnpEaCVbDbTDgzpijO6sX3rno")

logging.basicConfig(level=logging.INFO)


# --- ОБРАБОТКА ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text

        remember(user_input)
        update_state(state, user_input)

        reply = ai_generate(user_input, state)

        if not reply:
            reply = "..."

        dialog_memory.append(user_input)
        dialog_memory.append(reply)

        if len(dialog_memory) > 6:
            dialog_memory.pop(0)

        await update.message.reply_text(reply)

    except Exception as e:
        print("Ошибка:", e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я здесь.")


# --- ЗАПУСК ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling(drop_pending_updates=True)
    app.run_polling()


if __name__ == "__main__":
    main()
