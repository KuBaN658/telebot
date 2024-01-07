from aiogram import Router, F
from aiogram.types import Message, ContentType, FSInputFile
from keyboards.keyboards import yes_no_kb
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU
from services.services import add_photo, is_second
from model.transfer_style import device




# Инициализируем роутер уровня модуля
router: Router = Router()
DATA: dict = dict()

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=yes_no_kb)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/help'],
                         reply_markup=yes_no_kb)


# Этот хэндлер срабатывает на согласие пользователя играть в игру
@router.message(F.text == LEXICON_RU['yes_button'])
async def process_yes_answer(message: Message) -> None:
    await message.answer(text=LEXICON_RU['yes'])


# Этот хэндлер срабатывает на отказ пользователя играть в игру
@router.message(F.text == LEXICON_RU['no_button'])
async def process_no_answer(message: Message) -> None:
    await message.answer(text=LEXICON_RU['no'])


# Этот хэндлер срабатывает на отправку фотографий
@router.message(F.content_type == ContentType.PHOTO)
async def send_photo(message: Message) -> None:
    second: bool = is_second(user_id=message.from_user.id, data=DATA)
    if second:
        await message.answer(text=f'{LEXICON_RU["wait"]}')

    add_photo(
        user_id=message.from_user.id, 
        photo=message.photo, 
        data=DATA,
        is_second=second
    )

    if second:
        photo = FSInputFile(f"static/{message.from_user.id}.png")

        await message.answer_photo(photo=photo)
    else:
        await message.answer(text=f'{LEXICON_RU["first"]}')
