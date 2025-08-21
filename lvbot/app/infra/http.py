import aiohttp
import httpx
from contextlib import asynccontextmanager

# общий aiohttp-сессионник для GET к твоему API
@asynccontextmanager
async def aiohttp_session():
    async with aiohttp.ClientSession() as session:
        yield session

# httpx клиент — для инлайн-выдачи (короткоживущий)
@asynccontextmanager
async def httpx_client():
    async with httpx.AsyncClient(timeout=10) as client:
        yield client
