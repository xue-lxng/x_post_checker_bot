import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from loguru import logger

from config import BOT_TOKEN, DB_URL
from core.db.database_handler import DatabaseHandler
from core.utils.scheduler import scheduler
from routers import commands


async def main() -> None:
    logger.info("Starting bot")

    scheduler.start()

    dp = Dispatcher()
    bot = Bot(token=BOT_TOKEN)
    bot_data = await bot.get_me()
    logger.info(
        f"Bot started as {bot_data.first_name} with username {bot_data.username}"
    )

    db = DatabaseHandler(DB_URL)

    await db.init()

    dp["db"] = db
    dp.include_routers(
        commands.router,
    )

    bot_commands = [
        BotCommand(command="/start", description="Запуск / перезапуск бота 🚀"),
    ]
    await bot.set_my_commands(bot_commands)

    logger.info("Bot commands set")
    await logger.complete()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
