import asyncio
from aiogram import Dispatcher, Bot
from data.config import TOKEN
import logging
from loguru import logger
from handlers import user_start, load_data, agents, user, admins


async def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.add("debug.log", format="{time} {level} {message}",
               level="DEBUG", rotation="1 week", compression="zip")
    dp = Dispatcher()
    bot = Bot(TOKEN, parse_mode="HTML")
    dp.include_router(load_data.router)
    dp.include_router(agents.router)
    dp.include_router(admins.router)
    dp.include_router(user.router)
    dp.include_router(user_start.router)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    print("Бот запущен")
    asyncio.run(main())
