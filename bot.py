import discord
from discord.ext import commands, tasks

from config import TOKEN, ALERT_CHANNEL_ID, CHECK_INTERVAL
from database import *
from markets import get_market_price, get_spread, search_skins
bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents.default()
)

@bot.event
async def on_ready():
    init()
    await bot.tree.sync()
    checker.start()
    print("CS2 Market Bot online")

@bot.tree.command(name="price")
async def price(interaction: discord.Interaction, skin: str):
    await interaction.response.defer(thinking=True)

    try:
        price = await get_market_price(skin)

        if price == 0:
            await interaction.followup.send(
                f"❌ Skin jsem nenašel: **{skin}**\n"
                f"Zkus přesný název, třeba: `AK-47 | Redline (Field-Tested)`"
            )
            return

        await interaction.followup.send(
            f"💎 **{skin}**\n💰 Cena: **{price} Kč**"
        )

    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Chyba při načítání ceny:\n```{e}```"
        )
        @bot.tree.command(name="search", description="Vyhledá podobné CS2 skiny na CSFloat")
async def search(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)

    results = await search_skins(query)

    if not results:
        await interaction.followup.send(
            f"❌ Nic jsem nenašel pro: **{query}**\n"
            f"Zkus třeba: `AK-47 | Redline` nebo `M9 Bayonet`"
        )
        return

    text = ""

    for item in results[:10]:
        text += f"💎 **{item['name']}**\n"
        text += f"💰 {item['price_czk']} Kč\n\n"

    await interaction.followup.send(
        f"🔎 Výsledky pro: **{query}**\n\n{text}"
    )
@bot.tree.command(name="watch")
async def watch(interaction: discord.Interaction, skin: str):
    await interaction.response.defer(ephemeral=True)

    try:
        add_watch(interaction.user.id, skin)

        await interaction.followup.send(
            f"👀 Sleduji: **{skin}**",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Chyba při ukládání skinu:\n```{e}```",
            ephemeral=True
        )
@bot.tree.command(name="unwatch")
async def unwatch(interaction: discord.Interaction, skin:str):
    remove_watch(interaction.user.id, skin)
    await interaction.response.send_message(
        f"❌ Přestal jsem sledovat {skin}"
    )

@bot.tree.command(name="watchlist")
async def watchlist(interaction: discord.Interaction):
    items = get_user_watches(interaction.user.id)
    await interaction.response.send_message(
        "📋 Sleduješ:\n" + ("\n".join(items) if items else "Nic")
    )

@tasks.loop(seconds=CHECK_INTERVAL)
async def checker():
    for row in get_all():
        wid, user, skin, old = row
        new = await get_market_price(skin)

        if old and abs(new-old) > 500:
            u = await bot.fetch_user(user)
            await u.send(
                f"🚨 ALERT\n{skin}\n{old} Kč → {new} Kč"
            )

        update_price(wid,new)

bot.run(TOKEN)
