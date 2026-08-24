import os
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

SETTINGS_FILE = "user_settings.json"

CATEGORIES = ["BA", "BB", "AB", "AC"]


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


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
    text = (
        "Salam! 👋\n\n"
        "DİM imtahanlarında hansı kateqoriyanı izləmək istəyirsiniz?\n\n"
        "Aşağıdan seçim edin:"
    )

    await update.message.reply_text(
        text,
        reply_markup=category_keyboard()
    )


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("cat_", "")

    user_id = str(query.from_user.id)

    settings = load_settings()
    settings[user_id] = category
    save_settings(settings)

    category_name = "Bütün kateqoriyalar" if category == "ALL" else category

    keyboard = [
        [
            InlineKeyboardButton(
                "⚙️ Seçimi dəyiş",
                callback_data="change_category"
            )
        ]
    ]

    await query.edit_message_text(
        f"✅ Seçiminiz yadda saxlanıldı.\n\n"
        f"📌 İzlənən kateqoriya: {category_name}\n\n"
        f"Boş yer yarandıqda sizə xəbər veriləcək.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def change_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Yeni kateqoriyanı seçin:",
        reply_markup=category_keyboard()
    )


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        CallbackQueryHandler(
            choose_category,
            pattern=r"^cat_"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            change_category,
            pattern=r"^change_category$"
        )
    )

    print("Telegram bot başladı...")
    application.run_polling()


if __name__ == "__main__":
    main()
