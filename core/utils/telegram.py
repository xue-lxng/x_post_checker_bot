from aiogram.client.session import aiohttp

from config import BOT_TOKEN


async def send_message(chat_id: str, text: str):
    message_data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=message_data,
        ) as response:
            json_data = await response.json()
            return json_data
