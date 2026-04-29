import random
import os
import requests

# --- ХАРАКТЕР ---
personality = {
    "curiosity": random.uniform(0.4, 0.9),
    "talkativeness": random.uniform(0.4, 0.9),
    "emotionality": random.uniform(0.3, 0.8),
}

# --- СОСТОЯНИЕ ---
state = {
    "mood": 0.0,
    "interest": 0.5,
}

dialog_memory = []
memory_keywords = {}

# --- ОЧИСТКА СЛОВ ---
def clean_word(word):
    return word.strip(".,!?()[]\"'").lower()


# --- ПАМЯТЬ ---
def remember(user_input):
    global dialog_memory

    dialog_memory.append(user_input)
    if len(dialog_memory) > 6:
        dialog_memory.pop(0)

    for word in user_input.split():
        word = clean_word(word)

        if len(word) > 4:
            memory_keywords[word] = memory_keywords.get(word, 0) + 1

    # забывание
    for word in list(memory_keywords.keys()):
        memory_keywords[word] *= 0.9
        if memory_keywords[word] < 0.3:
            del memory_keywords[word]


# --- СОСТОЯНИЕ ---
def update_state(state, user_input):
    text = user_input.lower()

    if "привет" in text:
        state["mood"] += 0.2
        state["interest"] += 0.2
    elif "плохо" in text:
        state["mood"] -= 0.3
    else:
        state["mood"] -= 0.02

    state["mood"] = max(-1, min(1, state["mood"]))
    state["interest"] = max(0, min(1, state["interest"]))


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


def get_memory_word():
    if not memory_keywords:
        return None

    return random.choice(list(memory_keywords.keys()))


# --- ГЕНЕРАЦИЯ ---
def ai_generate(user_input, state):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
    "model": "qwen/qwen2.5:free",
    "messages": [
        {"role": "system", "content": "Ты странный, немного живой ИИ. Отвечай коротко и иногда необычно."},
        {"role": "user", "content": user_input}
    ]
            },
            timeout=15
        )

        print("STATUS:", response.status_code)
        print("TEXT:", response.text)

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("Ошибка API:", e)
        return "Ошибка API, смотри логи"

    return sentence
