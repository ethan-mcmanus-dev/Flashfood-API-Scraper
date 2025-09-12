import json
import time
import random
import argparse
import sys
import requests

STORAGE_FILE = "storage.json"

ITEMS_URL = "https://app.shopper.flashfood.com/api/v1/items/?storeIds=5d0bd76f8894a4ebbfd704bf"

STORES_URL = "https://app.shopper.flashfood.com/api/v1/stores?storesWithItemsLimit=10&includeItems=true&searchLatitude=50.915480109207884&searchLongitude=-114.11682218146578&userLocationLatitude=50.915480109207884&userLocationLongitude=-114.11682218146578&maxDistance=75000"



headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-CA",
    "Connection": "keep-alive",
    "flashfood-app-info": "app/shopper,appversion/3.2.6,appbuild/35155,os/ios,osversion/18.6.1,devicemodel/Apple_iPhone14_5,deviceid/unknown",
    "User-Agent": "Flashfood/35155 CFNetwork/3826.600.41 Darwin/24.6.0",
    "x-ff-api-key": "wEqsr63WozvJwNV4XKPv",
}

# ------------------------------
# Helpers for JSON storage
# ------------------------------
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"stores": {}}
    except json.JSONDecodeError:
        return {"stores": {}}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def fake_api_get_store(store_id):
    url = f"https://app.shopper.flashfood.com/api/v1/items/?storeIds={store_id}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching items: {response.status_code}")
        return None

    try:
        data = response.json()
        return data
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Raw text:", response.text)
        return None



# ------------------------------
# Compare old vs new
# ------------------------------
def diff_items(old_items, new_items):
    if old_items != None:
        old_names = {item["name"] for item in old_items}
        return [item for item in new_items if item["name"] not in old_names]
    return new_items


# ------------------------------
# Main heartbeat loop
# ------------------------------
def run(interval_seconds):
    while True:
        print("🔄 Checking for updates...")

        # 1. Load old data
        old_data = load_json(STORAGE_FILE)
        new_data = {"stores": {}}

        # 2. Iterate over each known store
        tracked_stores = old_data["stores"].keys()
        for store_id in tracked_stores:
            response = fake_api_get_store(store_id)

            if not response or "data" not in response:
                print(f"⚠️ No data for store {store_id}")
                continue

            store_name = old_data["stores"][store_id]["name"]
            items = response["data"][store_id]

            old_items = old_data["stores"].get(store_id, {}).get("items", [])

            new_items = diff_items(old_items, items)

            # Notify if new items appear
            for item in new_items:
                print(f"🆕 New item at {store_name}: {item['name']} - ${item['price']} - {item['quantityAvailable']} available")

            # Save latest snapshot for this store
            new_data["stores"][store_id] = {
                "name": store_name,
                "items": items
            }

        # 3. Save fresh snapshot
        save_json(STORAGE_FILE, new_data)

        # 4. Wait for next check
        time.sleep(interval_seconds)


# ------------------------------
# New function: show nearest store (mocked)
# ------------------------------
def nearest_store(lat, lon):

    url = (
        f"https://app.shopper.flashfood.com/api/v1/stores"
        f"?storesWithItemsLimit={1}"
        f"&includeItems=false"
        f"&searchLatitude={lat}"
        f"&searchLongitude={lon}"
        f"&userLocationLatitude={lat}"
        f"&userLocationLongitude={lon}"
        f"&maxDistance={75000}"
    )

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        return None

    store_info = response.json().get("data", [{}])[0]
    if not store_info:
        print("⚠️ No store found.")
        return None

    add_store(store_info["id"], store_info["name"])



def add_store(store_id, store_name):
    """Directly add a store to storage.json"""
    data = load_json(STORAGE_FILE)

    if store_id in data["stores"]:
        print(f"⚠️ Store {store_id} already exists in storage.")
    else:
        data["stores"][store_id] = {
            "name": store_name,
            "items": []  # start with no items
        }
        save_json(STORAGE_FILE, data)
        print(f"✅ Added store {store_name} ({store_id}) to storage.")



# ------------------------------
# CLI entrypoint
# ------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flashfood Tracker CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Default "run" command
    run_parser = subparsers.add_parser("run", help="Run tracker loop")
    run_parser.add_argument("--interval", type=int, default=600,
                            help="Seconds between checks (default 600)")

    # Nearest store command
    nearest_parser = subparsers.add_parser("nearest", help="Find nearest store")
    nearest_parser.add_argument("--lat", type=float)
    nearest_parser.add_argument("--lon", type=float)

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        run(args.interval if "interval" in args else 600)
    elif args.command == "nearest":
        nearest_store(lat=args.lat, lon=args.lon)
    else:
        parser.print_help()
        sys.exit(1)
