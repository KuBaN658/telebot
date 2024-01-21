from aiogram import Router
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU
from keyboards.keyboards import yes_no_kb

# Инициализируем роутер уровня модуля
router = Router()

# Хэндлер для сообщений, которые не попали в другие хэндлеры
@router.message()
async def send_answer(message: Message) -> None:
    await message.answer(text=LEXICON_RU['other_answer'])
    await message.answer(text=LEXICON_RU['/help'],
                         reply_markup=yes_no_kb)