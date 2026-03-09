import asyncio

from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
from bot.handlers import start, feedback

from database.session import init_db


async def main():

    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(feedback.router)

    await init_db()

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())