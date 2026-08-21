import requests
import urllib3

# Test məqsədilə SSL xəbərdarlığını gizlədirik
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

print("\n--- Səhifənin ilk 2000 simvolu ---\n")
print(response.text[:2000])
