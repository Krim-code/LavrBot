import re
from urllib.parse import urljoin
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ...config import get_settings
from ...infra.http import aiohttp_session
from ...utils.url import to_public

router = Router(name="catalog")

@router.callback_query(lambda c: c.data.startswith("brand_"))
async def brand_info_callback(callback: CallbackQuery):
    s = get_settings()
    brand_id = int(callback.data.replace("brand_", ""))

    async with aiohttp_session() as session:
        async with session.get(f"{s.API_BASE_URL}/api/brands/{brand_id}/") as resp:
            brand = await resp.json()
        async with session.get(f"{s.API_BASE_URL}/api/brands/{brand_id}/categories/") as resp:
            categories = await resp.json()

    await callback.message.answer(f"<b>{brand['name']}</b>\n\n{brand.get('description','')}", parse_mode="HTML")

    keyboard: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for i, cat in enumerate(categories):
        row.append(InlineKeyboardButton(text=cat["name"], callback_data=f"cat_{cat['id']}_brand_{brand_id}"))
        if (i + 1) % 3 == 0:
            keyboard.append(row); row = []
    if row:
        keyboard.append(row)

    if brand.get("archive"):
        full_url = to_public(brand["archive"], s.PUBLIC_BASE_URL)
        keyboard.append([InlineKeyboardButton(text="📥 Скачать всю библиотеку 3D моделей", url=full_url)])

    keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="go_main_menu")])
    await callback.message.answer("Выберите категорию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("cat_"))
async def show_products_by_category(callback: CallbackQuery):
    s = get_settings()
    match = re.match(r"cat_(\d+)_brand_(\d+)(?:_page_(\d+))?", callback.data)
    if not match:
        await callback.answer("Ошибка в данных категории.", show_alert=True); return

    cat_id, brand_id, page_str = match.groups()
    page = int(page_str) if page_str else 1

    async with aiohttp_session() as session:
        url = f"{s.API_BASE_URL}/api/products/?brand_id={brand_id}&category_id={cat_id}&page={page}"
        async with session.get(url) as resp:
            data = await resp.json()

    products = data.get("results", []) if isinstance(data, dict) else data
    if not products:
        await callback.message.edit_text("❌ В этой категории пока нет товаров."); await callback.answer(); return

    blocks: list[str] = []
    for p in products:
        text = (
            f"<b>{p['title']}</b>\n"
            f"Артикул: <code>{p['article']}</code>\n"
            f"{p.get('description','')}\n"
        )
        files = p.get("files", [])
        if files:
            dl = files[0].get("file")
            if dl:
                dl_public = to_public(dl, s.PUBLIC_BASE_URL)
                text += f"\n<a href='{dl_public}'>📥 Скачать</a>"
                blocks.append(text)

    final_text = "\n\n".join(blocks)

    nav_row: list[InlineKeyboardButton] = []
    if data.get("previous"):
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"cat_{cat_id}_brand_{brand_id}_page_{page-1}"))
    if data.get("next"):
        nav_row.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"cat_{cat_id}_brand_{brand_id}_page_{page+1}"))

    control_row = [
        InlineKeyboardButton(text="🔙 К категориям", callback_data=f"brand_{brand_id}"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="go_main_menu"),
    ]

    inline_keyboard: list[list[InlineKeyboardButton]] = []
    if nav_row:
        inline_keyboard.append(nav_row)
    inline_keyboard.append(control_row)

    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    try:
        await callback.message.edit_text(final_text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        await callback.message.answer(final_text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)

    await callback.answer()

@router.callback_query(F.data == "ask_question")
async def handle_question_placeholder(callback: CallbackQuery):
    await callback.message.answer("🛠 Интеграция с Bitrix24 скоро подъедет. Следи за апдейтами!")
    await callback.answer()
