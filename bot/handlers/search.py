from aiogram import Router, F, types
from aiogram.types import (
    CallbackQuery,
    InlineQueryResultArticle, InputTextMessageContent
)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import httpx
import html

from config import API_BASE_URL

router = Router()


class SearchState(StatesGroup):
    waiting_for_article = State()


# Кнопка из главного меню
@router.callback_query(F.data == "search_article")
async def ask_for_article(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔎 Введите артикул товара:")
    await state.set_state(SearchState.waiting_for_article)
    await callback.answer()


@router.inline_query()
async def inline_article_search(inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    if not query:
        return

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_BASE_URL}/api/products/?search={query}")
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            data = []

    results = []
    items = data.get("results", data)
    for product in items[:10]:
        title = product["title"]
        article = product["article"]
        brand = product["brand"]["name"]
        category = product["category"]["name"]
        description = product.get("description", "")

        files = product.get("files", [])
        download_url = files[0].get("file") if files else None

        text = (
            f"<b>{html.escape(title)}</b>\n"
            f"Артикул: <code>{html.escape(article)}</code>\n"
            f"Бренд: {html.escape(brand)}\n"
            f"Категория: {html.escape(category)}\n\n"
            f"{html.escape(description)}"
        )

        reply_markup = None
        if download_url:
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="📥 Скачать", url=download_url)]]
            )

        results.append(
            InlineQueryResultArticle(
                id=str(product["id"]),
                title=f"{title} [{article}]",
                description=f"{brand} — {category}",
                input_message_content=InputTextMessageContent(
                    message_text=text,
                    parse_mode="HTML"
                ),
                reply_markup=reply_markup
            )
        )

    await inline_query.answer(results, cache_time=1)