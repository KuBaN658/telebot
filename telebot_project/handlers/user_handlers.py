from aiogram import Router, F
from aiogram.types import Message, ContentType, FSInputFile
from keyboards.keyboards import yes_no_kb, choice_style_kb
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU
from model.transfer_style import device
from aiogram.fsm.context import FSMContext
from utils.states import States
from services.services import model, StyleTransfer


# Инициализируем роутер уровня модуля
router: Router = Router()
DATA: dict = dict()

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=yes_no_kb)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def cmd_help(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/help'],
                         reply_markup=yes_no_kb)


# Этот хэндлер срабатывает на согласие пользователя играть в игру
@router.message(F.text == LEXICON_RU['yes_button'])
async def process_yes_answer(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON_RU['yes'], 
                         reply_markup=choice_style_kb)
    await state.set_state(States.yes)


# Этот хэндлер срабатывает на отказ пользователя играть в игру
@router.message(F.text == LEXICON_RU['no_button'])
async def process_no_answer(message: Message) -> None:
    await message.answer(text=LEXICON_RU['no'])


@router.message(F.text == LEXICON_RU['oil_button'], States.yes)
async def process_oil_answer(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON_RU['send_photo'])
    await state.set_state(States.oil)


@router.message(F.text == LEXICON_RU['my_button'], States.yes)
async def process_oil_answer(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON_RU['send_style'])
    await state.set_state(States.my_style)


@router.message(F.content_type == ContentType.PHOTO, States.my_style)
async def send_photo(message: Message, state: FSMContext) -> None:
    image = StyleTransfer.take_pil_image(message.photo[-1].file_id)
    image.save(f'images/{message.from_user.id}.jpg')
    await message.answer(text=LEXICON_RU['send_photo'])
    await state.set_state(States.my_content)


@router.message(F.content_type == ContentType.PHOTO, States.oil)
async def send_photo(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON_RU['wait'])
    image = model(message.photo[-1], 'images/oil_style.jpg')
    image.save(f'static/{message.from_user.id}.png', format='PNG')
    photo = FSInputFile(f"static/{message.from_user.id}.png")
    await message.answer_photo(photo=photo)
    await state.set_state(States.yes)



@router.message(F.content_type == ContentType.PHOTO, States.my_content)
async def send_photo(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON_RU['wait'])
    image = model(message.photo[-1], f'images/{message.from_user.id}.jpg')
    image.save(f'static/{message.from_user.id}.png', format='PNG')
    photo = FSInputFile(f"static/{message.from_user.id}.png")
    await message.answer_photo(photo=photo)
    await state.set_state(States.yes)


