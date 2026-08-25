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

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

SETTINGS_FILE = "user_settings.json"


def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def github_file_url(filename):
    return (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPOSITORY}/contents/{filename}"
    )


def load_github_file(filename):
    response = requests.get(
        github_file_url(filename),
        headers=github_headers(),
        timeout=30,
    )

    if response.status_code == 404:
        return {}, None

    response.raise_for_status()

    data = response.json()

    content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    return json.loads(content), data["sha"]


def send_telegram(chat_id, message):
    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
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

    # =========================================================
    # 1. Telegram istifadəçilərinin seçimlərini GitHub-dan oxuyuruq
    # =========================================================

    settings, _ = load_github_file(
        SETTINGS_FILE
    )

    if not settings:
        print(
            "Heç bir Telegram istifadəçisi tapılmadı."
        )
        return

    print(
        "Telegram istifadəçi sayı:",
        len(settings)
    )

    # =========================================================
    # 2. DİM səhifəsini yükləyirik
    # =========================================================

    response = requests.get(
        DIM_URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        verify=False,
    )

    print(
        "Status:",
        response.status_code
    )

    response.raise_for_status()

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

    # =========================================================
    # 3. Bütün imtahan məlumatlarını toplayırıq
    # =========================================================

    all_exams = []

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

        try:
            available = int(
                available_text
            )
        except ValueError:
            available = 0

        all_exams.append({
            "exam_date": exam_date,
            "registration_date": registration_date,
            "last_date": last_date,
            "capacity": capacity,
            "registered": registered,
            "available": available,
            "location": location,
            "groups": groups,
            "registration": registration,
        })

    print(
        "Toplanan imtahan məlumatı:",
        len(all_exams)
    )

    # =========================================================
    # 4. HƏR İSTİFADƏÇİ ÜÇÜN ayrıca bildiriş hazırlayırıq
    # =========================================================

    for user_id, selected_category in settings.items():

        print()
        print(
            "----------------------------------------"
        )

        print(
            "İstifadəçi:",
            user_id
        )

        print(
            "Kateqoriya:",
            selected_category
        )

        # -----------------------------------------------------
        # 4.1. Bu istifadəçinin kateqoriyasına uyğun imtahanlar
        # -----------------------------------------------------

        matching_exams = []

        for exam in all_exams:

            if not category_matches(
                selected_category,
                exam["groups"]
            ):
                continue

            matching_exams.append(
                exam
            )

        print(
            "Uyğun imtahan sayı:",
            len(matching_exams)
        )

        # -----------------------------------------------------
        # 4.2. Heç bir uyğun imtahan yoxdursa
        # -----------------------------------------------------

        if not matching_exams:

            message = (
                f"🔴 {selected_category} üzrə "
                "hazırda uyğun imtahan tapılmadı."
            )

            try:
                send_telegram(
                    user_id,
                    message
                )

                print(
                    "Telegram: uyğun imtahan yoxdur."
                )

            except Exception as e:

                print(
                    "Telegram göndərmə xətası:",
                    user_id,
                    e
                )

            continue

        # -----------------------------------------------------
        # 4.3. Boş yerləri yoxlayırıq
        # -----------------------------------------------------

        has_available = False

        message_lines = [
            f"📊 {selected_category} üzrə DİM vəziyyəti",
            ""
        ]

        for exam in matching_exams:

            if exam["available"] > 0:

                has_available = True

                message_lines.extend([
                    "🟢 BOŞ YER VAR",
                    f"📅 {exam['exam_date']}",
                    f"👥 Qruplar: {exam['groups']}",
                    f"🟢 Boş yer: {exam['available']}",
                    f"👥 Ümumi yer: {exam['capacity']}",
                    f"📝 Qeydiyyatda: {exam['registered']}",
                    f"📍 {exam['location']}",
                    ""
                ])

        # -----------------------------------------------------
        # 4.4. Boş yer yoxdursa
        # -----------------------------------------------------

        if not has_available:

            message = (
                f"🔴 {selected_category} üzrə "
                "hazırda boş yer yoxdur."
            )

            try:
                send_telegram(
                    user_id,
                    message
                )

                print(
                    "Telegram: boş yer yoxdur."
                )

            except Exception as e:

                print(
                    "Telegram göndərmə xətası:",
                    user_id,
                    e
                )

            continue

        # -----------------------------------------------------
        # 4.5. Boş yer varsa bildiriş göndəririk
        # -----------------------------------------------------

        message_lines.append(
            "⏰ DİM məlumatı avtomatik yoxlanıldı."
        )

        message = "\n".join(
            message_lines
        )

        try:

            send_telegram(
                user_id,
                message
            )

            print(
                "Telegram: boş yer bildirişi göndərildi."
            )

        except Exception as e:

            print(
                "Telegram göndərmə xətası:",
                user_id,
                e
            )


if __name__ == "__main__":
    main()
