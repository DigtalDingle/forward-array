from fastapi import FastAPI, Query
import requests

app = FastAPI()

# Master symbol → CoinGecko ID map
COIN_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ZEC": "zcash",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "TRX": "tron",
    "TON": "the-open-network",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "STX": "blockstack",
    "LTC": "litecoin",
    "ATOM": "cosmos",
    "OP": "optimism",
    "ARB": "arbitrum",
    "INJ": "injective-protocol",
    "NEAR": "near",
    "ETC": "ethereum-classic",
    "APT": "aptos",
    "SEI": "sei-network",
    "MATIC": "matic-network",
    "FTM": "fantom"
}

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"


@app.get("/market/batch")
def market_batch(symbols: str = Query(..., description="Comma-separated list of symbols")):
    sym_list = [s.strip().upper() for s in symbols.split(",")]

    # Map symbols → CoinGecko IDs (skip unknown)
    valid_ids = []
    symbol_id_map = {}

    for sym in sym_list:
        if sym in COIN_MAP:
            cid = COIN_MAP[sym]
            valid_ids.append(cid)
            symbol_id_map[sym] = cid

    if not valid_ids:
        return {"prices": []}

    # Query CoinGecko
    params = {"ids": ",".join(valid_ids), "vs_currencies": "usd"}
    response = requests.get(COINGECKO_URL, params=params)
    data = response.json()

    prices = []

    # Safe extraction: skip missing/null entries
    for sym in sym_list:
        cid = symbol_id_map.get(sym)
        if cid is None:
            continue

        price = data.get(cid, {}).get("usd", None)

        if price is None:
            # Skip null or missing data so API never breaks
            continue

        prices.append({"symbol": sym, "price": price})

    return {"prices": prices}