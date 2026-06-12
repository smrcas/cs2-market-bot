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
        "limit": 1,
        "sort_by": "lowest_price"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(CSFLOAT_URL, headers=headers, params=params) as response:
            text = await response.text()

            if response.status != 200:
                print("CSFloat chyba:", response.status, text)
                return 0

            data = await response.json()

    listings = data.get("data", [])

    if not listings:
        print(f"Skin nenalezen: {skin}")
        return 0

    item = listings[0]

    price = item.get("price", 0)

    if price == 0:
        return 0

    price_usd = price / 100
    price_czk = round(price_usd * 23)

    return price_czk


async def get_spread(skin: str):
    csfloat_price = await get_market_price(skin)
    buff_price = 0

    return csfloat_price, buff_price, csfloat_price - buff_price