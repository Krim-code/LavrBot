from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from ..keyboards.start_keyboard import main_menu_keyboard, get_brands, InlineKeyboardMarkup, InlineKeyboardButton

router = Router(name="start")

@router.message(Command("start"))
async def cmd_start(message: Message):
    kb = await main_menu_keyboard()
    await message.answer("Привет! 👋\nЭто бот LavrPro. Выбирай бренд или жми поиск.", reply_markup=kb)

@router.callback_query(F.data == "go_main_menu")
async def show_main_menu(callback: CallbackQuery):
    kb = await main_menu_keyboard()
    await callback.message.edit_text("Выбери бренд или действие:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "brands_regular")
async def show_regular(callback: CallbackQuery):
    regular = await get_brands(premium=False)
    keyboard: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for i, brand in enumerate(regular):
        row.append(InlineKeyboardButton(text=brand['name'], callback_data=f"brand_{brand['id']}"))
        if (i + 1) % 2 == 0:
            keyboard.append(row); row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="go_main_menu")])
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()
