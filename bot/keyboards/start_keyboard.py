from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp

from config import API_BASE_URL

def start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Старт", callback_data="go_main_menu")]
    ])

async def main_menu_keyboard():
    premium = await get_brands(premium=True)
    keyboard = []

    row = []
    for i, brand in enumerate(premium):
        row.append(InlineKeyboardButton(
            text=brand['name'],
            callback_data=f"brand_{brand['id']}"
        ))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="Остальные бренды", callback_data="brands_regular")])
    keyboard.append([InlineKeyboardButton(text="Задать вопрос по товару", callback_data="ask_question")])
    keyboard.append([InlineKeyboardButton(
    text="Поиск по артикулу",
    switch_inline_query_current_chat=""
)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_brands(premium=True):
    endpoint = f"{API_BASE_URL}/api/brands/premium/" if premium else f"{API_BASE_URL}/api/brands/regular/"
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as resp:
            return await resp.json()
        
