import logging
import requests
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CommandHandler,
    filters,
)
from telegram.request import HTTPXRequest

from main import ai_generate, state, remember, update_state, dialog_memory

# --- НАСТРОЙКИ ---
TOKEN = os.getenv("8207302663:AAG46mdKUzQnpEaCVbDbTDgzpijO6sX3rno")
PROXY_URL = "socks5://107.173.123.87:10808"

logging.basicConfig(level=logging.INFO)

# --- ПРОВЕРКА ПРОКСИ ---
def check_proxy():
    try:
        proxies = {
            "http": PROXY_URL,
            "https": PROXY_URL
        }

        r = requests.get("https://api.telegram.org", proxies=proxies, timeout=10)
        print("Прокси работает:", r.status_code)
    except Exception as e:
        print("Прокси НЕ работает:", e)


# --- ОБРАБОТКА СООБЩЕНИЙ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я здесь.")


# --- ЗАПУСК ---
def main():
    check_proxy()

    request = HTTPXRequest(proxy_url=PROXY_URL)

    app = ApplicationBuilder() \
        .token(TOKEN) \
        .request(request) \
        .build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
