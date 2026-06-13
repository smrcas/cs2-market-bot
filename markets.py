import os
import aiohttp
from dotenv import load_dotenv

print("✅ MARKETS.PY SE NAČETL", flush=True)

load_dotenv()

CSFLOAT_API_KEY = os.getenv("CSFLOAT_API_KEY", "").strip()

CSFLOAT_URL = "https://csfloat.com/api/v1/listings"


async def get_market_price(skin: str) -> int:

    print(f"✅ GET_MARKET_PRICE VOLÁNO PRO: {skin}", flush=True)

    headers = {}

    if CSFLOAT_API_KEY:
        headers["Authorization"] = CSFLOAT_API_KEY

    params = {
        "market_hash_name": skin,
        "limit": 5,
        "sort_by": "lowest_price"
    }

    timeout = aiohttp.ClientTimeout(total=15)

    try:

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.get(
                CSFLOAT_URL,
                headers=headers,
                params=params
            ) as response:

                print(
                    f"✅ STATUS: {response.status}",
                    flush=True
                )

                text = await response.text()

                print(
                    f"✅ ODPOVED: {text[:1000]}",
                    flush=True
                )

                if response.status != 200:
                    return 0

                data = await response.json()

        print(
            f"✅ JSON: {data}",
            flush=True
        )

        listings = data.get("data", [])

        if not listings:

            print(
                f"❌ SKIN NENALEZEN: {skin}",
                flush=True
            )

            return 0

        item = listings[0]

        print(
            f"✅ ITEM: {item}",
            flush=True
        )

        price = item.get("price", 0)

        if not price:
            return 0

        price_usd = float(price) / 100

        print(
            f"✅ USD CENA: {price_usd}",
            flush=True
        )

        price_czk = round(
            price_usd * 23
        )

        print(
            f"✅ CZK CENA: {price_czk}",
            flush=True
        )

        return price_czk

    except Exception as e:

        print(
            f"❌ CHYBA CSFLOAT: {e}",
            flush=True
        )

        return 0


async def get_spread(skin: str):

    csfloat_price = await get_market_price(skin)

    buff_price = 0

    return (
        csfloat_price,
        buff_price,
        csfloat_price - buff_price
    )
async def search_skins(query: str, limit: int = 10):
    headers = {}

    if CSFLOAT_API_KEY:
        headers["Authorization"] = CSFLOAT_API_KEY

    params = {
        "market_hash_name": query,
        "limit": limit
    }

    timeout = aiohttp.ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                CSFLOAT_URL,
                headers=headers,
                params=params
            ) as response:

                if response.status != 200:
                    text = await response.text()
                    print(f"❌ SEARCH CHYBA {response.status}: {text}", flush=True)
                    return []

                data = await response.json()

        listings = data.get("data", [])

        results = []

        for item in listings:
            name = item.get("item_name", "Neznámý skin")
            wear = item.get("wear_name", "")
            price = item.get("price", 0)

            full_name = f"{name} ({wear})" if wear else name
            price_czk = round((price / 100) * 23) if price else 0

            results.append({
                "name": full_name,
                "price_czk": price_czk
            })

        return results

    except Exception as e:
        print(f"❌ SEARCH ERROR: {e}", flush=True)
        return []
