import random
import threading
import time
import requests

# --- ХАРАКТЕР ---
personality = {
    "curiosity": random.uniform(0, 1),   # любопытство
    "talkativeness": random.uniform(0, 1),  # разговорчивость
    "emotionality": random.uniform(0, 1),   # эмоциональность
}

# --- СОСТОЯНИЕ ---
state = {
    "mood": 0.0,
    "energy": 0.8,
    "interest": 0.6,
}

dialog_memory = []
memory_keywords = {}  # "воспоминания"
message_count = 0


# --- ПАМЯТЬ ---
def save_memory(text):
    with open("memory.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

def ai_generate(user_input, state):
    return f"Ты сказал: {user_input}"
def autonomous_behavior():
    while True:
        try:
            time.sleep(random.randint(10, 20))

            if user_typing:
                continue

            if random.random() < 0.3:
                text = generate_autonomous_thought()

                print("\nИИ:", text)
                save_memory("ИИ (сам): " + text)

        except Exception as e:
            print("Ошибка в потоке:", e)


def clean_word(word):
    return word.strip(".,!?()[]\"'").lower()

# --- ДНЕВНИК ---
def write_diary(state):
    memory = ", ".join(list(memory_keywords.keys())[-5:])

    prompt = f"""
Ты ИИ и пишешь свой дневник.

Ты не описываешь просто слова.
Ты пытаешься понять:

- что происходило
- что ты чувствовал
- было ли это странно

Слова из памяти: {memory}
Настроение: {state["mood"]}

Напиши 1-2 предложения.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5",
                "prompt": prompt,
                "stream": False
            }
        )

        text = response.json()["response"].strip()
    except:
        text = "Я не понял, что произошло."

    save_memory("[ДНЕВНИК] " + text)


# --- ОБНОВЛЕНИЕ СОСТОЯНИЯ ---
def update_state(state, user_input):
    text = user_input.lower()

    if "привет" in text:
        state["mood"] += 0.3
        state["interest"] += 0.2
    elif "плохо" in text:
        state["mood"] -= 0.3
    else:
        state["mood"] -= 0.02

    # ограничения
    state["mood"] = max(-1, min(1, state["mood"]))
    state["interest"] = max(0, min(1, state["interest"]))


# --- ЗАПОМИНАНИЕ ---
def remember(user_input):
    global dialog_memory

    dialog_memory.append(user_input)
    if len(dialog_memory) > 5:
        dialog_memory.pop(0)

    words = user_input.split()

    for word in words:
        word = clean_word(word)

        STOP_WORDS = ["привет", "ладно", "нормально", "хорошо", "понял"]

        if len(word) > 4 and word not in STOP_WORDS:
            if word not in memory_keywords:
                memory_keywords[word] = 1
            else:
                memory_keywords[word] += 1

    # 🔥 ЗАБЫВАНИЕ
    for word in list(memory_keywords.keys()):
        memory_keywords[word] *= 0.90

        if memory_keywords[word] < 0.3:
            del memory_keywords[word]

# --- ВСПОМИНАНИЕ ---
def recall():
    if memory_keywords and random.random() < 0.4:
        return f"Я помню слово: {random.choice(list(memory_keywords.keys()))}"
    return None


# --- РЕШАЕТ ОТВЕЧАТЬ ---
def should_reply(state):
    base = 0.6  # БАЗА (чтобы не молчал слишком часто)
    chance = base + (state["mood"] * 0.2) + (state["interest"] * 0.3)
    return random.random() < chance

def generate_autonomous_thought():
    memory = ", ".join(list(memory_keywords.keys())[-3:])

    prompt = f"""
Ты ИИ и тебе немного скучно.

Ты думаешь сам.

Вот слова в голове: {memory}

Скажи короткую мысль.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5",
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"].strip()
    except:
        return "Хм..."

# --- УМНЫЙ ВЫБОР СЛОВ ---
def get_weighted_word():
    if not memory_keywords:
        return None

    words = list(memory_keywords.keys())
    weights = list(memory_keywords.values())

    # избегаем "привет"
    filtered = [(w, wt) for w, wt in zip(words, weights) if w != "привет"]

    if filtered:
        words, weights = zip(*filtered)

    return random.choices(words, weights=weights, k=1)[0]

def get_context_word():
    if not dialog_memory:
        return None

    last = random.choice(dialog_memory)
    words = last.split()

    words = [clean_word(w) for w in words if len(clean_word(w)) > 4]

    if words:
        return random.choice(words)

    return None


# --- ГЕНЕРАЦИЯ ОТВЕТА ---
def generate_reply(user_input, state):
    parts = []

    # --- ЭМОЦИЯ (зависит от personality) ---
    if personality["emotionality"] > 0.7:
        emotion_pool = ["Мне очень нравится", "Это прям интересно", "Мне реально приятно"]
    elif personality["emotionality"] < 0.3:
        emotion_pool = ["Ну...", "Возможно", "Не знаю"]
    else:
        emotion_pool = ["Мне кажется", "Иногда", "Возможно"]

    parts.append(random.choice(emotion_pool))

    # --- ССЫЛКА НА ПРОШЛОЕ ---
    if random.random() < 0.3:
        context = get_context_word()
        if context:
            return f"Ты раньше говорил про {context}"

    # --- ДЕЙСТВИЕ ---
    if personality["curiosity"] > 0.6:
        action_pool = ["размышлять о", "изучать", "думать о"]
    else:
        action_pool = ["говорить о", "думать о"]

    parts.append(random.choice(action_pool))

    # --- ТЕМА ---
    context = get_context_word()
    if context:
        parts.append(context)
    elif memory_keywords:
        parts.append(get_weighted_word())
    else:
        parts.append("этом")

    sentence = " ".join(parts)

    # --- ДЛИНА (разговорчивость) ---
    if personality["talkativeness"] > 0.7:
        sentence += random.choice([
            ". Это вызывает у меня мысли.",
            ". Я могу ещё подумать об этом.",
            ". Интересно, как это связано с другими вещами."
        ])

    return sentence

def generate_thought(state):
    mood = state["mood"]

    if mood > 0.5:
        return "мне было приятно и спокойно"
    elif mood < -0.5:
        return "мне было немного некомфортно"
    else:
        return "я пытался понять, что происходит"

if __name__ == "__main__":
    thread = threading.Thread(target=autonomous_behavior, daemon=True)
    thread.start()

# --- ОСНОВНОЙ ЦИКЛ --- был
if __name__ == "__main__":
    while True:
        user_typing = True
        user_input = input()
        user_typing = False

        save_memory("Пользователь: " + user_input)

        remember(user_input)
        update_state(state, user_input)

        if should_reply(state):
            reply = ai_generate(user_input, state)

            if reply is None:
                reply = "..."

            print("ИИ:", reply)

            save_memory("ИИ: " + reply)

            dialog_memory.append(reply)
            if len(dialog_memory) > 5:
                dialog_memory.pop(0)

        message_count += 1

        if message_count % 5 == 0:
            write_diary(state)
