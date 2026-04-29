import random

# --- СОСТОЯНИЕ ---
state = {
    "mood": 0.0,
    "energy": 0.8,
    "interest": 0.6,
}

dialog_memory = []
memory_keywords = {}

# --- ПРОСТАЯ ГЕНЕРАЦИЯ ---
def ai_generate(user_input, state):
    return f"Ты сказал: {user_input}. Интересно."


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

    state["mood"] = max(-1, min(1, state["mood"]))
    state["interest"] = max(0, min(1, state["interest"]))


# --- ЗАПОМИНАНИЕ ---
def remember(user_input):
    global dialog_memory

    dialog_memory.append(user_input)

    if len(dialog_memory) > 5:
        dialog_memory.pop(0)
