import os
import json
import base64
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

DIM_URL = "https://exidmet.dim.gov.az/dqq/ImtQeyd"

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

SETTINGS_FILE = "user_settings.json"


def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def load_settings():
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPOSITORY}/contents/{SETTINGS_FILE}"
    )

    response = requests.get(
        url,
        headers=github_headers(),
        timeout=30,
    )

    if response.status_code == 404:
        return {}

    response.raise_for_status()

    data = response.json()

    content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    return json.loads(content)


def send_telegram(message):
    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        },
        timeout=30,
    )

    response.raise_for_status()


def category_matches(selected_category, groups):
    if selected_category == "ALL":
        return True

    return selected_category in groups


def main():

    # 1. Telegram istifadəçisinin seçimini oxu
    settings = load_settings()

    if not settings:
        print("Heç bir Telegram kateqoriyası seçilməyib.")
        return

    # Hazırda TELEGRAM_CHAT_ID istifadə edirik
    user_id = str(TELEGRAM_CHAT_ID)

    selected_category = settings.get(user_id)

    if not selected_category:
        print(
            "TELEGRAM_CHAT_ID üçün kateqoriya seçimi tapılmadı."
        )
        return

    print(
        "Seçilmiş kateqoriya:",
        selected_category
    )

    # 2. DİM səhifəsini götür
    response = requests.get(
        DIM_URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        verify=False
    )

    print("Status:", response.status_code)

    response.raise_for_status()

    # 3. HTML-i oxu
    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    rows = soup.select(
        "table tbody tr"
    )

    print(
        "Tapılan imtahan sayı:",
        len(rows)
    )

    # 4. İmtahanları yoxla
    for row in rows:

        cells = row.find_all("td")

        if len(cells) < 9:
            continue

        exam_date = cells[0].get_text(
            " ",
            strip=True
        )

        registration_date = cells[1].get_text(
            " ",
            strip=True
        )

        last_date = cells[2].get_text(
            " ",
            strip=True
        )

        capacity = cells[3].get_text(
            " ",
            strip=True
        )

        registered = cells[4].get_text(
            " ",
            strip=True
        )

        available_text = cells[5].get_text(
            " ",
            strip=True
        )

        location = cells[6].get_text(
            " ",
            strip=True
        )

        groups = cells[7].get_text(
            " ",
            strip=True
        )

        registration = cells[8].get_text(
            " ",
            strip=True
        )

        # 5. Boş yer sayını rəqəmə çevir
        try:
            available = int(
                available_text
            )
        except ValueError:
            available = 0

        # 6. Seçilmiş kateqoriyaya uyğunluq
        if not category_matches(
            selected_category,
            groups
        ):
            continue

        print(
            "Uyğun imtahan:",
            exam_date,
            "|",
            groups,
            "| Boş:",
            available
        )

        # 7. Boş yer yoxdursa mesaj göndərmə
        if available <= 0:
            continue

        # 8. Telegram mesajı
        message = (
            "🚨 DİM-də boş yer var!\n\n"
            f"📅 İmtahan: {exam_date}\n"
            f"📌 Kateqoriya: {groups}\n"
            f"🟢 Boş yer: {available}\n"
            f"👥 Ümumi yer: {capacity}\n"
            f"📝 Qeydiyyatda: {registered}\n\n"
            f"📍 Ünvan:\n{location}\n\n"
            f"⏰ Qeydiyyat: {registration_date}\n"
            f"⛔ Son tarix: {last_date}\n\n"
            f"🔗 Status: {registration}"
        )

        send_telegram(message)

        print(
            "Telegram bildirişi göndərildi."
        )


if __name__ == "__main__":
    main()
