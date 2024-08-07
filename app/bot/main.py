import asyncio
import os

import loguru
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from handlers.routing import get_main_router
from core.config import settings
from mongo.engine import mongo_manager
from core.container import Container
import handlers


async def main(container: Container):
    """Запуск бота."""
    load_dotenv()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties())

    dp = Dispatcher()
    dp.include_router(get_main_router())

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        mongo_manager.drop_database()
        mongo_manager.db_client.close()


if __name__ == "__main__":
    container = Container()
    loguru.logger.info('Bot is starting')
    container.wire(modules=[handlers.start, handlers.resume, handlers.state])
    asyncio.run(main(container=container))
