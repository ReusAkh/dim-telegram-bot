import requests
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
print("Səhifənin ölçüsü:", len(response.text))

html = response.text

# HTML-i hissələrə bölüb daha rahat yoxlayırıq
print("\n--- HTML-in son 5000 simvolu ---\n")
print(html[-5000:])
