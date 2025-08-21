import html
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from ...config import get_settings
from ...infra.http import httpx_client
from ...utils.url import to_public
from ..states.search_state import SearchState
from aiogram.fsm.context import FSMContext

router = Router(name="search")

# если когда-то вернёшь отдельную кнопку "search_article"
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

    s = get_settings()
    async with httpx_client() as client:
        try:
            resp = await client.get(f"{s.API_BASE_URL}/api/products/", params={"search": query})
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            data = []

    results: list[InlineQueryResultArticle] = []
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

        download_url = files[0].get("file") if files else None

        reply_markup = None
        if download_url:
            public_url = to_public(download_url, s.PUBLIC_BASE_URL)
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="📥 Скачать", url=public_url)]]
            )

        results.append(
            InlineQueryResultArticle(
                id=str(product["id"]),
                title=f"{title} [{article}]",
                description=f"{brand} — {category}",
                input_message_content=InputTextMessageContent(message_text=text, parse_mode="HTML"),
                reply_markup=reply_markup,
            )
        )

    await inline_query.answer(results, cache_time=1)
