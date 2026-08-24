import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DIM_URL = "https://exidmet.dim.gov.az/dqq/ImtQeyd"

response = requests.get(
    DIM_URL,
    timeout=30,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    verify=False
)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

# Səhifədəki bütün cədvəl sətrlərini tapırıq
rows = soup.select("table tbody tr")

print("Tapılan imtahan sayı:", len(rows))
print()

for row in rows:
    cells = row.find_all("td")

    if len(cells) < 9:
        continue

    exam_date = cells[0].get_text(" ", strip=True)
    registration_date = cells[1].get_text(" ", strip=True)
    last_date = cells[2].get_text(" ", strip=True)

    capacity = cells[3].get_text(" ", strip=True)
    registered = cells[4].get_text(" ", strip=True)
    available = cells[5].get_text(" ", strip=True)

    location = cells[6].get_text(" ", strip=True)
    groups = cells[7].get_text(" ", strip=True)
    registration = cells[8].get_text(" ", strip=True)

    print("=" * 60)
    print("İmtahan:", exam_date)
    print("Qeydiyyat:", registration_date)
    print("Son tarix:", last_date)
    print("Ümumi yer:", capacity)
    print("Qeydiyyatda:", registered)
    print("Boş yer:", available)
    print("Ünvan:", location)
    print("Qruplar:", groups)
    print("Status:", registration)
