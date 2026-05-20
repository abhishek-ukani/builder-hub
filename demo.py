import requests

BASE_URL = "https://eu5.fusionsolar.huawei.com"

payload = {
    "userName": "EFIpladot",
    "systemCode": "Hofit1996"
}

r = requests.post(
    f"{BASE_URL}/thirdData/login",
    json=payload
)

print(r.json())