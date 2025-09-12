import requests
import json

#url = "https://app.shopper.flashfood.com/api/v1/items/?storeIds=5d0bd76f8894a4ebbfd704bf"

url = "https://app.shopper.flashfood.com/api/v1/stores?storesWithItemsLimit=10&includeItems=true&searchLatitude=50.915480109207884&searchLongitude=-114.11682218146578&userLocationLatitude=50.915480109207884&userLocationLongitude=-114.11682218146578&maxDistance=75000"

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-CA",
    "Connection": "keep-alive",
    "flashfood-app-info": "app/shopper,appversion/3.2.6,appbuild/35155,os/ios,osversion/18.6.1,devicemodel/Apple_iPhone14_5,deviceid/unknown",
    "User-Agent": "Flashfood/35155 CFNetwork/3826.600.41 Darwin/24.6.0",
    "x-ff-api-key": "wEqsr63WozvJwNV4XKPv",
}

store_id = "5d0bd76f8894a4ebbfd704bf"

response = requests.get(url, headers=headers)

if(response.status_code != 200):
    print("Error fetching data")
    exit()

print("Status code:", response.status_code)

try:
    data = response.json()

    # Count items for that store
    items = data["data"][store_id]
    print(f"Number of items: {len(items)}")

    # Optional: list the names
    for item in items:
        print("-", item["name"], "for $", item["price"])

except Exception:
    print("Raw response text:\n", response.text)
