import csv
import time
import requests
from datetime import datetime

ASSETS = [
    "BTC","ETH","SOL","ZEC","BNB","XRP","ADA","DOGE","TRX","TON",
    "AVAX","LINK","UNI","STX","LTC","ATOM","OP","ARB","INJ","NEAR",
    "ETC","APT","SEI","MATIC","FTM"
]

API_URL = "http://127.0.0.1:8000/market/batch?symbols=" + ",".join(ASSETS)
LOG_FILE = r"C:\Gains\data\price_log.csv"


# Ensure header exists
def ensure_header():
    try:
        with open(LOG_FILE, "r") as f:
            first = f.readline().strip()
            if first.startswith("timestamp"):
                return
    except FileNotFoundError:
        pass

    header = ["timestamp"] + ASSETS
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    print("[INFO] Created new CSV header.")


# Poll the API
def poll_prices():
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        data = r.json()

        result = {}
        for item in data.get("prices", []):
            sym = item.get("symbol")
            price = item.get("price")
            if sym and price is not None:
                result[sym] = price

        return result

    except Exception as e:
        print("[ERROR] Poll error:", e)
        return None


# Write a row
def write_row(prices):
    timestamp = datetime.utcnow().isoformat()
    row = [timestamp]

    for sym in ASSETS:
        row.append(prices.get(sym, ""))

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    print(f"[LOGGED] {timestamp} -> written to price_log.csv")


# Main loop
def main():
    ensure_header()
    print("[START] Poller running every 60 seconds")

    while True:
        prices = poll_prices()

        if prices:
            write_row(prices)
        else:
            print("[WARN] No valid data this cycle")

        time.sleep(60)


# REQUIRED — or nothing runs
if __name__ == "__main__":
    main()