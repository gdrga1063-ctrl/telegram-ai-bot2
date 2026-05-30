import base64
import random
import os
import re
import requests
import json

from github_memory import update_github_diary
from datetime import datetime, date
from memory_manager import memory
from memory_manager import process_user_input

from memory_manager import (
    brain,
    load_memory,
    save_memory,
    remember_dialogue,
    update_brain,
    get_memory_context,
)

# --- ЧТЕНИЕ ПАМЯТИ ---
load_memory()

# --- ХАРАКТЕР ---
today_seed = date.today().toordinal()
random.seed(today_seed)

personality = {
    "curiosity": random.uniform(0.4, 0.9),
    "talkativeness": random.uniform(0.4, 0.9),
    "emotionality": random.uniform(0.3, 0.8),
}

dialog_memory = []
DIARY_FILE = "diary.json"

# --- ОЧИСТКА СЛОВ ---
def clean_word(word):
    return word.strip(".,!?()[]\"'").lower()

# --- ДНЕВНИК ---
def load_diary():
    if not os.path.exists(DIARY_FILE):
        return []

    try:
        with open(DIARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_diary(user_input, reply):
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_input,
        "reply": reply
    }

    # локально
    diary = load_diary()
    diary.append(entry)

    if len(diary) > 30:
        diary.pop(0)

    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=2)

    # GitHub
    update_github_diary(entry)

# --- ВСПОМОГАТЕЛЬНОЕ ---
def get_context_word():
    if not dialog_memory:
        return None

    last = dialog_memory[-1]  # последнее сообщение (важно!)
    words = last.split()

    words = [
        clean_word(w)
        for w in words
        if len(clean_word(w)) > 4
        and clean_word(w) not in ["круто", "ладно", "понял", "привет"]
    ]

    return random.choice(words) if words else None

# --- ГЕНЕРАЦИЯ ---
def ai_generate(user_input):
    process_user_input(user_input)
    
    try:

        # --- SYSTEM PROMPT ---
        messages = [
            {
                "role": "system",
                "content": f"""
            Ты дружелюбный ИИ с характером.
            
            Твое текущее состояние:
            mood = {brain["mood"]}
            interest = {brain["interest"]}
            loneliness = {brain["loneliness"]}

            Известные факты о пользователе:
            {memory["facts_about_user"]}
            
            Правила:
            - Отвечай естественно
            - Говори как живой собеседник
            - Не повторяйся
            - Не будь слишком официальным
            - Иногда шути
            - Если человек говорит о чувствах — реагируй тепло
            - Не придумывай ложные воспоминания о себе
            - Если у тебя нет опыта — говори об этом честно
            - Не утверждай что делал что-то в реальном мире
            """
            }
        ]

        # --- ДОБАВЛЯЕМ ПАМЯТЬ ---
        for d in memory["dialogues"][-6:]:

            messages.append({
                "role": "user",
                "content": d["user"]
            })

            messages.append({
                "role": "assistant",
                "content": d["reply"]
            })

        # --- НОВОЕ СООБЩЕНИЕ ---
        messages.append({
            "role": "user",
            "content": user_input
        })

        # --- ЗАПРОС ---
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen3-32b",
                "messages": messages
            },
            timeout=15
        )

        print("STATUS:", response.status_code)
        print("TEXT:", response.text)

        data = response.json()

        if "error" in data:
            print("❌ API ERROR:", data["error"]["message"])
            return f"API ошибка: {data['error']['message']}"

        reply = data["choices"][0]["message"]["content"]

        # Убираем think
        reply = re.sub(
            r"<think>.*?</think>",
            "",
            reply,
            flags=re.DOTALL
        ).strip()

        # --- СОХРАНЯЕМ ---
        remember_dialogue(user_input, reply)
        save_diary(user_input, reply)

        return reply

    except Exception as e:
        print("Ошибка API:", e)
        return "Ошибка API, смотри логи"
