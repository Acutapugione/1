import asyncio
import logging
import sys
from os import getenv
from re import Match
from typing import Any, Dict
from keyboards import languages_menu
from settings import Settings
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


TOKEN = getenv("TOKEN") or "6166859922:AAHTelA_UwYNMc9-BCL8vcwWf4cMViu4IKc"


form_router = Router()


class Form(StatesGroup):
    name = State()
    language = State()
    task = State()
    price = State()


@form_router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Form.name)
    await message.answer(
        "Hello my potential customer! What's your name?",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def cmd_cancel(
    message: Message,
    state: FSMContext,
) -> None:
    curr_state = await state.get_state()

    if not curr_state:
        return

    logging.info("Cancelling state %r", curr_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.name)
async def process_name(
    message: Message,
    state: FSMContext,
) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.language)
    await message.answer(
        f"Greetings, {html.quote(message.text)}!\nWhat programming language did you prefer to task?",
        reply_markup=languages_menu,
    )


@form_router.message(Form.language, F.text.in_(Settings.LANGUAGES))
async def process_language(
    message: Message,
    state: FSMContext,
) -> None:
    await state.update_data(language=message.text)
    await state.set_state(Form.task)
    if message.text.casefold() == "python":
        await message.reply(
            "Python, you say? Im good in this, have a 5 years of experience. Good choise!😉"
        )
    await message.answer(
        "Please write some task for project you need.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.task)
async def process_task(
    message: Message,
    state: FSMContext,
) -> None:
    await state.update_data(task=message.text)
    await state.set_state(Form.price)
    await message.answer(
        "Please write price for this task.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.price, F.text.regexp(r"^(\d+)$").as_("digits"))
async def process_price(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.update_data(price=message.text)
    await state.clear()
    await show_summary(message, data)


@form_router.message(Form.price)
async def process_wrong_price(
    message: Message,
    state: FSMContext,
) -> None:
    await message.answer(
        "Please write price in only digits.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def show_summary(
    message: Message,
    data: Dict[str, Any],
) -> None:
    language =  data.get("language", "<smth unexpected>")
    await message.answer(
        f"Okey, task {html.italic(data.get('task'))} accepted!\nPrice: {html.quote(data.get('price'))}\nLanguage: {html.bold(data.get('language'))}",
        reply_markup=ReplyKeyboardRemove()
    )


async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
