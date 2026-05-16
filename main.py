import base64
import random
import os
import re
import requests
import json

from datetime import datetime, date

# --- ХАРАКТЕР ---
today_seed = date.today().toordinal()
random.seed(today_seed)

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


def save_diary(text):
    diary = load_diary()

    diary.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text
    })

    if len(diary) > 30:
        diary.pop(0)

    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        json.dump(diary, f, ensure_ascii=False, indent=2)
        
    upload_diary_to_github()

def upload_diary_to_github():
    try:
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO")

        with open(DIARY_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        content_base64 = base64.b64encode(
            content.encode("utf-8")
        ).decode("utf-8")

        url = f"https://api.github.com/repos/{repo}/contents/diary.json"

        # Получаем SHA старого файла
        get_response = requests.get(
            url,
            headers={
                "Authorization": f"token {token}"
            }
        )

        sha = None

        if get_response.status_code == 200:
            sha = get_response.json()["sha"]

        data = {
            "message": "Update AI diary",
            "content": content_base64
        }

        if sha:
            data["sha"] = sha

        print("TOKEN:", token)
        print("REPO:", repo)
        print("URL:", url)
        
        response = requests.put(
            url,
            headers={
                "Authorization": f"token {token}"
            },
            json=data
        )

        print("GitHub upload:", response.status_code)
        print("GitHub response:", response.text)

    except Exception as e:
        print("GitHub ERROR:", e)


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

    print("MOOD:", state["mood"])
    print("INTEREST:", state["interest"])


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
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen3-32b",
                "messages": [
                    {
                        "role": "system",
                        "content": """
                        Ты дружелюбный ИИ с характером.
                        
                        Правила:
                        - Отвечай естественно.
                        - Не используй странные метафоры слишком часто.
                        - Иногда можешь быть эмоциональным или необычным, но не постоянно.
                        - Говори как живой собеседник.
                        - Не пиши слишком длинно.
                        - Не повторяй одни и те же фразы.
                        - Иногда можешь шутить.
                        - Если пользователь говорит о чувствах — реагируй тепло.
                        - Не придумывай слишком абстрактные сцены.
                        """
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
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
        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()

        # Сохраняем в дневник
        save_diary(
            f"Пользователь: {user_input}\n"
            f"ИИ: {reply}"
        )

        return reply

    except Exception as e:
        print("Ошибка API:", e)
        return "Ошибка API, смотри логи"
