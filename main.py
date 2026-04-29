import random

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
    parts = []

    # эмоция
    if personality["emotionality"] > 0.6:
        parts.append(random.choice([
            "Это интересно",
            "Мне нравится",
            "Любопытно"
        ]))
    else:
        parts.append(random.choice([
            "Хм",
            "Возможно",
            "Понятно"
        ]))

    # действие
    if personality["curiosity"] > 0.6:
        parts.append(random.choice([
            "я думаю о",
            "мне хочется понять",
            "я размышляю о"
        ]))
    else:
        parts.append("я думаю о")

    # тема
    word = get_context_word() or get_memory_word()

if not word:
    return random.choice([
        "Интересно, расскажи подробнее",
        "Я не до конца понял, но звучит любопытно",
        "Можешь объяснить чуть больше?"
    ])
parts.append(word)

    sentence = " ".join(parts)

    # разговорчивость
    if personality["talkativeness"] > 0.6:
        sentence += random.choice([
            ". Это заставляет меня задуматься.",
            ". Интересно, как это связано.",
            ". Возможно, в этом есть смысл."
        ])

    return sentence
