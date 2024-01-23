from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon import LEXICON_RU

button_yes = KeyboardButton(text=LEXICON_RU['yes_button'])
button_no = KeyboardButton(text=LEXICON_RU['no_button'])
button_oil = KeyboardButton(text=LEXICON_RU['oil_button'])
button_my = KeyboardButton(text=LEXICON_RU['my_button'])
button_pencil = KeyboardButton(text=LEXICON_RU['pencil_button'])

yes_no_kb_builder = ReplyKeyboardBuilder()
choice_style_builder = ReplyKeyboardBuilder()

yes_no_kb_builder.row(button_yes, button_no, width=2)
choice_style_builder.row(button_oil, button_my, button_pencil, width=3)

# Создаем клавиатуры
yes_no_kb: ReplyKeyboardMarkup = yes_no_kb_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)

choice_style_kb: ReplyKeyboardMarkup = choice_style_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)