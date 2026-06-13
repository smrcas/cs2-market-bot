import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

CSFLOAT_API_KEY = os.getenv("CSFLOAT_API_KEY", "").strip()
CSFLOAT_URL = "https://csfloat.com/api/v1/listings"


async def get_market_price(skin: str) -> int:
    headers = {}

    if CSFLOAT_API_KEY:
        headers["Authorization"] = CSFLOAT_API_KEY

    params = {
        "market_hash_name": skin,
        "limit": 5,
        "sort_by": "lowest_price"
    }

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(CSFLOAT_URL, headers=headers, params=params) as response:
            data = await response.json()

            if response.status != 200:
                print("CSFloat chyba:", response.status, data)
                return 0

    listings = data.get("data", [])

    if not listings:
        print("Nenalezeno:", skin)
        return 0

    item = listings[0]

    print("DEBUG ITEM:", item)

    price_cents = item.get("price", 0)

    if not price_cents:
        return 0

    price_usd = price_cents / 100
    price_czk = round(price_usd * 23)

    return price_czk
