from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
# при желании воткнёшь RedisStorage

from ..config import get_settings

def create_bot() -> Bot:
    s = get_settings()
    return Bot(
        token=s.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

async def create_dispatcher() -> Dispatcher:
    storage = MemoryStorage()
    return Dispatcher(storage=storage)
