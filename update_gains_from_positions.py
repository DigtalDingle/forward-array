import csv
from pathlib import Path
import requests

# ------------------------------
# CONFIG
# ------------------------------

# Where the input/output files live (relative to C:\Gains)
ROOT_DIR = Path(__file__).resolve().parent.parent
GAINS_FILE = ROOT_DIR / "Gains.csv"
POSITIONS_FILE = ROOT_DIR / "data" / "positions.csv"

# Your starting principal per exchange (lock these in once)
STARTING_PRINCIPAL = {
    "coinbase": 1110.33,   # update if needed
    "binance": 119.63,     # update if needed
}

# Map tickers in positions.csv to CoinGecko IDs
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ZEC": "zcash",
    "ATOM": "cosmos",
    "USDT": "tether",
    "USDC": "usd-coin",
    "BNB": "binancecoin",
    # For PUMP, confirm its CoinGecko ID and put it here:
    # Example (you may need to adjust):
    "PUMP": "pump-fun",   # <-- change if CoinGecko uses a different id
}

# ------------------------------
# CORE LOGIC
# ------------------------------

def load_positions():
    if not POSITIONS_FILE.exists():
        raise FileNotFoundError(f"positions file not found: {POSITIONS_FILE}")

    positions = []
    with POSITIONS_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"exchange", "symbol", "units"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(
                f"positions.csv must have columns: {', '.join(sorted(required))}"
            )
        for row in reader:
            symbol = row["symbol"].strip().upper()
            exchange = row["exchange"].strip().lower()
            units = float(row["units"])
            positions.append(
                {"exchange": exchange, "symbol": symbol, "units": units}
            )
    return positions


def fetch_prices(symbols):
    missing = [s for s in symbols if s not in COINGECKO_IDS]
    if missing:
        raise ValueError(
            f"No CoinGecko ID mapping for symbols: {', '.join(missing)}. "
            f"Update COINGECKO_IDS in the script."
        )

    ids = [COINGECKO_IDS[s] for s in symbols]
    ids_param = ",".join(sorted(set(ids)))

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ids_param, "vs_currencies": "usd"}

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    prices = {}
    for sym in symbols:
        cg_id = COINGECKO_IDS[sym]
        if cg_id not in data or "usd" not in data[cg_id]:
            raise ValueError(f"Missing USD price for {sym} (id={cg_id})")
        prices[sym] = float(data[cg_id]["usd"])
    return prices


def compute_values(positions, prices):
    per_exchange = {}
    for pos in positions:
        ex = pos["exchange"]
        sym = pos["symbol"]
        units = pos["units"]
        price = prices.get(sym)
        if price is None:
            raise ValueError(f"No price found for symbol {sym}")
        value = units * price
        per_exchange[ex] = per_exchange.get(ex, 0.0) + value
    return per_exchange


def write_gains(values):
    # Ensure we always write exchanges in a stable order
    exchanges = sorted(STARTING_PRINCIPAL.keys())
    with GAINS_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["exchange", "starting_principal", "current_value"])
        for ex in exchanges:
            start = float(STARTING_PRINCIPAL[ex])
            current = float(values.get(ex, 0.0))
            writer.writerow([ex, f"{start:.2f}", f"{current:.2f}"])


def main():
    print(f"Using positions file: {POSITIONS_FILE}")
    print(f"Updating gains file:  {GAINS_FILE}")

    positions = load_positions()
    symbols = sorted({p["symbol"] for p in positions})
    print("Symbols found in positions.csv:", ", ".join(symbols))

    prices = fetch_prices(symbols)
    print("Latest prices (USD):")
    for sym in symbols:
        print(f"  {sym}: {prices[sym]:.4f}")

    values = compute_values(positions, prices)
    write_gains(values)

    print("\nPer-exchange summary:")
    for ex, start in STARTING_PRINCIPAL.items():
        current = values.get(ex, 0.0)
        pnl = current - start
        print(f"  {ex}: current={current:.2f}, start={start:.2f}, pnl={pnl:.2f}")

    print("\nGains.csv updated successfully.")


if __name__ == "__main__":
    main()
