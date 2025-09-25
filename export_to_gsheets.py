import asyncio
from aiogram import Bot

API_TOKEN = "8033548959:AAEtHzV-TecfYAnpUBkkhKW8-ynnTPIk36k"

bot = Bot(token=API_TOKEN)

async def main():
    updates = await bot.get_updates()
    for u in updates:
        print(u)

asyncio.run(main())