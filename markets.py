import os
import aiohttp
from dotenv import load_dotenv

print("✅ MARKETS.PY SE NAČETL", flush=True)

load_dotenv()

CSFLOAT_API_KEY = os.getenv("CSFLOAT_API_KEY", "").strip()
CSFLOAT_URL = "https://csfloat.com/api/v1/listings"
USD_TO_CZK = 23


def headers():
    h = {}
    if CSFLOAT_API_KEY:
        h["Authorization"] = CSFLOAT_API_KEY
    return h


def price_to_czk(price_cents):
    if not price_cents:
        return 0
    return round((float(price_cents) / 100) * USD_TO_CZK)


def item_full_name(item):
    data = item.get("item", item)

    market_hash = data.get("market_hash_name")
    if market_hash:
        return market_hash

    name = data.get("item_name", "Neznámý skin")
    wear = data.get("wear_name", "")
    return f"{name} ({wear})" if wear else name


async def fetch_listings(params):
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(
            CSFLOAT_URL,
            headers=headers(),
            params=params
        ) as response:
            text = await response.text()
            print(f"✅ STATUS: {response.status}", flush=True)
            print(f"✅ ODPOVED: {text[:700]}", flush=True)

            if response.status != 200:
                return []

            data = await response.json()

    if isinstance(data, dict):
        return data.get("data", [])

    if isinstance(data, list):
        return data

    return []


async def get_market_price(skin: str) -> int:
    print(f"✅ GET_MARKET_PRICE VOLÁNO PRO: {skin}", flush=True)

    params = {
        "market_hash_name": skin,
        "limit": 5,
        "sort_by": "lowest_price"
    }

    listings = await fetch_listings(params)

    if not listings:
        print(f"❌ SKIN NENALEZEN: {skin}", flush=True)
        return 0

    item = listings[0]
    price = item.get("price", 0)

    czk = price_to_czk(price)
    print(f"✅ CENA CZK: {czk}", flush=True)

    return czk


async def get_spread(skin: str):
    csfloat_price = await get_market_price(skin)
    buff_price = 0
    return csfloat_price, buff_price, csfloat_price - buff_price


async def search_skins(query: str, limit: int = 10):
    print(f"🔎 SEARCH VOLÁNO PRO: {query}", flush=True)

    params = {
        "limit": 50,
        "sort_by": "lowest_price"
    }

    listings = await fetch_listings(params)

    words = query.lower().replace("|", " ").split()
    results = []

    for item in listings:
        name = item_full_name(item)
        name_lower = name.lower()

        if all(word in name_lower for word in words):
            price = item.get("price", 0)

            results.append({
                "name": name,
                "price_czk": price_to_czk(price)
            })

    return results[:limit]
