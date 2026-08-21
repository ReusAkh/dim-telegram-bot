import requests

DIM_URL = "https://exidmet.dim.gov.az/dqq/ImtQeyd"

response = requests.get(
    DIM_URL,
    timeout=30,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

print("Status:", response.status_code)
print("Səhifənin ölçüsü:", len(response.text))

print("\n--- Səhifənin ilk 1000 simvolu ---\n")
print(response.text[:1000])
