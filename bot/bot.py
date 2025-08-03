from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

import asyncio

from handlers import start,search



async def main():
    bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(search.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
