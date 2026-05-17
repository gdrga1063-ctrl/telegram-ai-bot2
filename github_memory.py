from github import Github
import os
import json

TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "gdrga1063-ctrl/telegram-ai-bot2"

g = Github(TOKEN)

FILE_PATH = "diary.json"


def update_github_diary(entry):
    try:
        repo = g.get_repo(REPO_NAME)

        try:
            file = repo.get_contents(FILE_PATH)

            content = json.loads(
                file.decoded_content.decode()
            )

        except:
            content = []

        content.append(entry)

        new_content = json.dumps(
            content,
            ensure_ascii=False,
            indent=2
        )

        try:
            repo.update_file(
                FILE_PATH,
                "Обновление дневника ИИ",
                new_content,
                file.sha
            )

        except:
            repo.create_file(
                FILE_PATH,
                "Создание дневника ИИ",
                new_content
            )

        print("Дневник обновлен в GitHub")

    except Exception as e:
        print("Ошибка GitHub:", e)
