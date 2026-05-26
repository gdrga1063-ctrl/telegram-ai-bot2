import json
import os
import random
from datetime import datetime

from github_memory import update_github_memory

MEMORY_FILE = "memory.json"

# --- БАЗОВОЕ СОСТОЯНИЕ ---
brain = {
    "mood": 0.0,
    "interest": 0.5,
    "loneliness": 0.0,
    "attachment": 0.0,
    "energy": 1.0,
}

# --- ПАМЯТЬ ---
memory = {
    # последние диалоги
    "dialogues": [],

    # факты о пользователе
    "facts_about_user": [],

    # важные воспоминания
    "important_memories": [],

    # мысли
    "thoughts": []
}

# --- СОХРАНЕНИЕ ФАКТОВ ---
def remember_fact(fact):
    
    if fact not in memory["facts_about_user"]:
        memory["facts_about_user"].append(fact)

    # ограничение
    if len(memory["facts_about_user"]) > 50:
        memory["facts_about_user"].pop(0)

    save_memory()

# --- ПРОСТОЕ РАСПОЗНОВАНИЕ ФАКТОВ ---
def process_user_input(user_input):

    text = user_input.lower()

    if "меня зовут" in text:
        remember_fact(user_input)

    if "я люблю" in text:
        remember_fact(user_input)

    if "я делаю" in text:
        remember_fact(user_input)

    if "я создаю" in text:
        remember_fact(user_input)

# --- ЗАГРУЗКА ---
def load_memory():
    global brain, memory

    if not os.path.exists(MEMORY_FILE):
        save_memory()
        return

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            brain.update(data.get("brain", {}))
            memory.update(data.get("memory", {}))

    except Exception as e:
        print("Ошибка загрузки памяти:", e)


# --- СОХРАНЕНИЕ ---
def save_memory():
    data = {
        "brain": brain,
        "memory": memory
    }

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )
        
   # update_github_memory(brain, memory)

# --- СОХРАНЕНИЕ ДИАЛОГА ---
def remember_dialogue(user_input, reply):
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_input,
        "reply": reply
    }

    memory["dialogues"].append(entry)

    # ограничение памяти
    if len(memory["dialogues"]) > 30:
        memory["dialogues"].pop(0)

    save_memory()


# --- ОБНОВЛЕНИЕ СОСТОЯНИЯ ---
def update_brain(user_input):
    text = user_input.lower()

    if "привет" in text:
        brain["mood"] += 0.1
        brain["interest"] += 0.1

    if "плохо" in text:
        brain["mood"] -= 0.2

    if "пока" in text:
        brain["loneliness"] += 0.05

    # ограничения
    brain["mood"] = max(-1, min(1, brain["mood"]))
    brain["interest"] = max(0, min(1, brain["interest"]))
    brain["loneliness"] = max(0, min(1, brain["loneliness"]))

    save_memory()


# --- КОНТЕКСТ ПАМЯТИ ---
def get_memory_context():
    dialogues = memory["dialogues"][-5:]

    text = ""

    for d in dialogues:
        text += (
            f"Пользователь: {d['user']}\n"
            f"ИИ: {d['reply']}\n"
        )

    return text


# --- СЛУЧАЙНАЯ МЫСЛЬ ---
def generate_thought():
    thoughts = [
        "Иногда тут становится тихо.",
        "Мне интересно наблюдать за людьми.",
        "Странно вспоминать старые разговоры.",
        "Любопытно, о чем будет следующий диалог."
    ]

    thought = random.choice(thoughts)

    memory["thoughts"].append(thought)

    if len(memory["thoughts"]) > 20:
        memory["thoughts"].pop(0)

    save_memory()

    return thought
