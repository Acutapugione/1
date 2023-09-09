from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import html
from settings import Settings

builder = ReplyKeyboardBuilder()
for item in Settings.LANGUAGES:
    builder.button(
        text=item
    )
    
builder.adjust(1, 2, 3, 4, 5, 6)
languages_menu = builder.as_markup(one_time_keyboard=True)