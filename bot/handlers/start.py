import re
from urllib.parse import urljoin
from aiogram import Router, F
from aiogram.filters import Command
from keyboards.start_keyboard import main_menu_keyboard
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp

from config import API_BASE_URL, PUBLIC_BASE


router = Router()
 # noqa: F704

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = await main_menu_keyboard() 
    await message.answer(
        "Привет! 👋\n Это бот LavrPro. Ты можешь выбрать интересующий бренд или начать поиск.",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "go_main_menu")
async def show_main_menu(callback: CallbackQuery):
    keyboard = await main_menu_keyboard()
    await callback.message.edit_text(
        text="Выбери бренд или действие:",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "brands_regular")
async def show_regular(callback: CallbackQuery):
    from keyboards.start_keyboard import get_brands
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    regular = await get_brands(premium=False)
    keyboard = []

    row = []
    for i, brand in enumerate(regular):
        row.append(InlineKeyboardButton(
            text=brand['name'],
            callback_data=f"brand_{brand['id']}"
        ))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="go_main_menu")])

    await callback.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    
    

@router.callback_query(lambda c: c.data.startswith("brand_"))
async def brand_info_callback(callback: CallbackQuery):
    brand_id = int(callback.data.replace("brand_", ""))

    async with aiohttp.ClientSession() as session:
        # Получаем инфу о бренде
        brand_url = f"{API_BASE_URL}/api/brands/{brand_id}/"
        categories_url = f"{API_BASE_URL}/api/brands/{brand_id}/categories/"

        async with session.get(brand_url) as resp:
            brand = await resp.json()

        async with session.get(categories_url) as resp:
            categories = await resp.json()

    await callback.message.answer(
        f"<b>{brand['name']}</b>\n\n{brand.get('description', '')}",
        parse_mode="HTML"
    )

    keyboard = []
    row = []
    for i, cat in enumerate(categories):
        row.append(InlineKeyboardButton(
            text=cat["name"],
            callback_data=f"cat_{cat['id']}_brand_{brand_id}"
         ))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
  
    
    if brand.get("archive"):
        archive_path = brand.get("archive")
        full_url = urljoin(PUBLIC_BASE, archive_path)
        keyboard.append([
            InlineKeyboardButton(
                text="📥 Скачать всю библиотеку 3D моделей",
                url=full_url
            )
        ])

    # 🔙 Навигация
    keyboard.append([
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="go_main_menu"
        )
    ])

    await callback.message.answer(
        "Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("cat_"))
async def show_products_by_category(callback: CallbackQuery):
    import re
    match = re.match(r"cat_(\d+)_brand_(\d+)(?:_page_(\d+))?", callback.data)
    if not match:
        await callback.answer("Ошибка в данных категории.", show_alert=True)
        return

    cat_id, brand_id, page_str = match.groups()
    page = int(page_str) if page_str else 1

    async with aiohttp.ClientSession() as session:
        url = f"{API_BASE_URL}/api/products/?brand_id={brand_id}&category_id={cat_id}&page={page}"
        async with session.get(url) as resp:
            data = await resp.json()

    products = data.get("results", []) if isinstance(data, dict) else data

    if not products:
        await callback.message.edit_text("❌ В этой категории пока нет товаров.")
        await callback.answer()
        return

    # Собираем текст
    product_texts = []
    for product in products:
        text = (
            f"<b>{product['title']}</b>\n"
            f"Артикул: <code>{product['article']}</code>\n"
            f"{product.get('description', '')}\n"
        )

        # Прикрутим первую ссылку из files (если есть)
        files = product.get("files", [])
        if files:
            download_url = files[0].get("file")
            if download_url:
                text += f"\n<a href='{download_url}'>📥 Скачать</a>"

        product_texts.append(text)

    # Соединяем всё одним сообщением
    final_text = "\n\n".join(product_texts)

    # Кнопки: пагинация + назад
    nav_row = []
    if data.get("previous"):
        nav_row.append(InlineKeyboardButton(
            text="⬅️ Назад", callback_data=f"cat_{cat_id}_brand_{brand_id}_page_{page - 1}"
        ))
    if data.get("next"):
        nav_row.append(InlineKeyboardButton(
            text="➡️ Далее", callback_data=f"cat_{cat_id}_brand_{brand_id}_page_{page + 1}"
        ))

    # Управление
    control_row = [
        InlineKeyboardButton(
            text="🔙 К категориям", callback_data=f"brand_{brand_id}"
        ),
        InlineKeyboardButton(
            text="🏠 Главное меню", callback_data="go_main_menu"
        )
    ]

    inline_keyboard = []

    if nav_row:
        inline_keyboard.append(nav_row)

    inline_keyboard.append(control_row)

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    # Обновляем текст сообщения (если поддерживается)
    try:
        await callback.message.edit_text(final_text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        # Если edit_text не сработал (например, старое сообщение), отправляем новое
        await callback.message.answer(final_text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)

    await callback.answer()


@router.callback_query(F.data == "ask_question")
async def handle_question_placeholder(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🛠 Возможность задать вопрос будет доступна в скором времени — мы готовим интеграцию с Bitrix24.\n\n"
        "Следи за обновлениями!"
    )
