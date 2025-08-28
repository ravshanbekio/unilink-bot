import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from commands import start, universities, apply, check_application, contact, about_us

load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(start.start_router)
dp.include_router(universities.universities_router)
dp.include_router(apply.apply_router)
dp.include_router(check_application.check_router)
dp.include_router(about_us.about_router)
dp.include_router(contact.contact_router)

async def main():
    """
        Start polling the bot
    """
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())