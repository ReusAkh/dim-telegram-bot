import os
import json
import base64
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

SETTINGS_FILE = "user_settings.json"

CATEGORIES = ["BA", "BB", "AB", "AC", "ALL"]


def github_api_url():
    return (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPOSITORY}/contents/{SETTINGS_FILE}"
    )


def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def load_settings():
    response = requests.get(
        github_api_url(),
        headers=github_headers(),
        timeout=30,
    )

    if response.status_code == 404:
        return {}, None

    response.raise_for_status()

    data = response.json()
    content = base64.b64decode(data["content"]).decode("utf-8")

    return json.loads(content), data["sha"]


def save_settings(settings, sha=None):
    content = json.dumps(
        settings,
        ensure_ascii=False,
        indent=2,
    )

    encoded = base64.b64encode(
        content.encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": "Telegram istifadəçi seçimini yenilə",
        "content": encoded,
        "branch": "main",
    }

    if sha:
        payload["sha"] = sha

    response = requests.put(
        github_api_url(),
        headers=github_headers(),
        json=payload,
        timeout=30,
    )

    response.raise_for_status()


def category_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("BA", callback_data="cat_BA"),
            InlineKeyboardButton("BB", callback_data="cat_BB"),
        ],
        [
            InlineKeyboardButton("AB", callback_data="cat_AB"),
            InlineKeyboardButton("AC", callback_data="cat_AC"),
        ],
        [
            InlineKeyboardButton("Hamısı", callback_data="cat_ALL"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salam! 👋\n\n"
        "İzləmək istədiyiniz kateqoriyanı seçin:",
        reply_markup=category_keyboard(),
    )


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("cat_", "")
    user_id = str(query.from_user.id)

    try:
        settings, sha = load_settings()

        settings[user_id] = category

        save_settings(settings, sha)

    except Exception as error:
        print("GitHub yaddaş xətası:", error)

        await query.edit_message_text(
            "❌ Seçimi yadda saxlamaq mümkün olmadı.\n"
            "Bir neçə saniyə sonra yenidən cəhd edin."
        )
        return

    category_name = (
        "Bütün kateqoriyalar"
        if category == "ALL"
        else category
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "⚙️ Seçimi dəyiş",
                callback_data="change_category",
            )
        ]
    ]

    await query.edit_message_text(
        f"✅ Seçiminiz yadda saxlanıldı.\n\n"
        f"📌 İzlənən kateqoriya: {category_name}\n\n"
        f"Boş yer yarananda sizə xəbər veriləcək.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def change_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Yeni kateqoriyanı seçin:",
        reply_markup=category_keyboard(),
    )


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(
            choose_category,
            pattern=r"^cat_",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            change_category,
            pattern=r"^change_category$",
        )
    )

    print("Telegram bot başladı...")
    application.run_polling()


if __name__ == "__main__":
    main()
