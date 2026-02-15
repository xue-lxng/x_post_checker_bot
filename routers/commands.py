import re

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.db.database_handler import DatabaseHandler

router = Router()


def strip_bot_suffix(text: str) -> str:
    """
    Return the command text without a trailing "@BotName" part
    that Telegram adds in groups, e.g. "/u_123@Meeting_Bot" -> "/u_123".
    """
    return text.split("@", 1)[0]


@router.message(Command("start"))
async def start_command_handler(
    message: Message, db: DatabaseHandler, state: FSMContext
) -> None:
    """Handle /start command by initializing user and sending greeting with the main menu."""
    await state.clear()

    user_language = message.from_user.language_code or "en"
    user = await db.create_or_get_user(
        user_tg_id=int(message.from_user.id),
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        language=user_language,
    )

    if not user.is_admin:
        await message.answer(
            "Нет доступа 🖕",
        )
        return

    await message.answer_sticker(
        "CAACAgIAAxkBAAEQeSZpif-pUCDbvPZcuAmmxo0S7BH7CgACQwADRA3PFyKsrFUWfp1hOgQ"
    )
    await message.answer(
        "Привет! Кратко по использованию:\n\n"
        "Добавить пост для отслеживания: `/add <tweet_url> <community_url>(необязательно)`\n"
        "Перестать отслеживать: `/remove <tweet_url>`\n"
        "Предоставить доступ к боту: `/allow <user_telegram_id>`",
        parse_mode=ParseMode.MARKDOWN,
    )


@router.message(Command("add"))
async def add_command_handler(message: Message, db: DatabaseHandler, state: FSMContext):
    command_data = message.text.split(" ")
    if len(command_data) < 2:
        await message.answer(
            "Добавить пост для отслеживания: `/add <tweet_url> <community_url>(необязательно)`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    tweet_url = command_data[1]
    tweet_id = re.search(r"/status/(\d+)", tweet_url).group(1)
    community_id = None
    if len(command_data) == 3:
        community_url = command_data[2]
        community_id = re.search(r"/communities/(\d+)", community_url).group(1)

    await db.add_tweet(
        tweet_url=tweet_url,
        tweet_id=tweet_id,
        community_id=community_id,
        user_id=message.from_user.id,
    )
    await message.answer("Окей, будем следить! 🦈")


@router.message(Command("remove"))
async def add_command_handler(message: Message, db: DatabaseHandler, state: FSMContext):
    command_data = message.text.split(" ")
    if len(command_data) < 2:
        await message.answer(
            "Перестать отслеживать пост: `/remove <tweet_url>`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    tweet_url = command_data[1]
    tweet_id = re.search(r"/status/(\d+)", tweet_url).group(1)

    await db.set_as_inactive(
        tweet_id=tweet_id,
        user_id=message.from_user.id,
    )
    await message.answer("Пока пока, пост! 🦈")


@router.message(Command("allow"))
async def invite_command_handler(
    message: Message, db: DatabaseHandler, state: FSMContext
):
    command_data = message.text.split(" ")
    if len(command_data) < 2:
        await message.answer(
            "Предоставить доступ к боту: `/allow <user_telegram_id>`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    user_to_allow_id = command_data[1]

    await db.update_user(user_tg_id=int(user_to_allow_id), is_admin=True)
    await message.answer(
        f"Доступ выдан пользователю {user_to_allow_id}"
    )
