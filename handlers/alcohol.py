from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from launch import dp
from texts import AVAILABLE_ALCOHOL_CATEGORIES, CHECK_TEXT, HELP_TEXT_ALCOHOL, AVAILABLE_ALCOHOL_MEASUREMENT_UNITS, \
    FINAL_TEXT
from database import db
import re


class OrderAlcohol(StatesGroup):
    waiting_for_alcohol_category = State()
    waiting_for_other = State()
    waiting_for_amount = State()


# step 1
@dp.message_handler(commands='alcohol', state='*')
async def alco_step_1(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in sorted(AVAILABLE_ALCOHOL_CATEGORIES):
        keyboard.add(category)
    await message.answer('Выбери категорию алкоголя', reply_markup=keyboard)
    await OrderAlcohol.waiting_for_alcohol_category.set()


# step 2
@dp.message_handler(state=OrderAlcohol.waiting_for_alcohol_category, content_types=types.ContentType.TEXT)
async def alco_step_2(message: types.Message, state: FSMContext):
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await OrderAlcohol.waiting_for_alcohol_category.set()
        return
    category = message.text.lower()
    if category not in AVAILABLE_ALCOHOL_CATEGORIES:
        await message.reply('Пожалуйста, не неси херню, используй клавиатуру ниже')
        return
    await state.update_data(chosen_alcohol=category)
    await message.answer(HELP_TEXT_ALCOHOL, reply_markup=types.ReplyKeyboardRemove())
    await OrderAlcohol.waiting_for_other.set()


# step 3
@dp.message_handler(state=OrderAlcohol.waiting_for_other, content_types=types.ContentType.TEXT)
async def alco_step_3(message: types.Message, state: FSMContext):
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await OrderAlcohol.waiting_for_other.set()
        return
    if not message.text.lower() == '/skip':
        await state.update_data(other=message.text.lower())
    await message.answer('Укажи количество')
    await OrderAlcohol.waiting_for_amount.set()


# step 4
@dp.message_handler(state=OrderAlcohol.waiting_for_amount, content_types=types.ContentType.TEXT)
async def alco_step_4(message: types.Message, state: FSMContext):
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await OrderAlcohol.waiting_for_amount.set()
        return
    for unit in AVAILABLE_ALCOHOL_MEASUREMENT_UNITS:
        if re.search(unit, message.text.lower()):
            break
    else:
        await message.answer(CHECK_TEXT)
        await OrderAlcohol.waiting_for_amount.set()
        return
    await state.update_data(amount=message.text.lower(), name=message.from_user.full_name)

    user_data = await state.get_data()
    await db.touch(user_data)

    await message.answer(FINAL_TEXT)
    await state.finish()
