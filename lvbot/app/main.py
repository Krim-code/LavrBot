import asyncio, logging
from aiogram import Dispatcher
from .logging import setup_logging
from .bot.factory import create_bot, create_dispatcher
from .bot.routers import start, catalog, search

async def _register(dp: Dispatcher):
    dp.include_routers(
        start.router,
        catalog.router,
        search.router,
    )

async def main():
    setup_logging()
    bot = create_bot()
    dp = await create_dispatcher()
    await _register(dp)
    logging.getLogger(__name__).info("LavrPro bot: starting polling…")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
