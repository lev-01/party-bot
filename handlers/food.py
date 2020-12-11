from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from launch import dp
from texts import AVAILABLE_FOOD_CATEGORIES, HELP_TEXT_FOOD, CHECK_TEXT, AVAILABLE_FOOD_MEASUREMENT_UNITS, FINAL_TEXT
import re


class OrderFood(StatesGroup):
    waiting_for_food_category = State()
    waiting_for_food_name = State()
    waiting_for_other = State()
    waiting_for_amount = State()


# step 1
@dp.message_handler(commands='food', state='*')
async def food_step_1(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in sorted(AVAILABLE_FOOD_CATEGORIES):
        keyboard.add(category)
    await message.answer('Выбери категорию еды', reply_markup=keyboard)
    await OrderFood.waiting_for_food_category.set()


# step 2
@dp.message_handler(state=OrderFood.waiting_for_food_category, content_types=types.ContentTypes.TEXT)
async def food_step_2(message: types.Message, state: FSMContext):
    category = message.text.lower()
    if category not in AVAILABLE_FOOD_CATEGORIES:
        await message.reply('Пожалуйста, не неси херню, используй клавиатуру ниже')
        return
    await state.update_data(chosen_food_category=category)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in sorted(AVAILABLE_FOOD_CATEGORIES.get(category)):
        keyboard.add(name)
    if category == 'мясо':
        await message.answer('Уточни, какое мясо ты хочешь', reply_markup=keyboard)
    elif category == 'рыба':
        await message.answer('Уточни, какую рыбу ты хочешь', reply_markup=keyboard)
    elif category == 'молочка':
        await message.answer('Уточни, какую молочку ты хочешь', reply_markup=keyboard)
    elif category == 'овощи':
        await message.answer('Уточни, какие овощи ты хочешь', reply_markup=keyboard)
    elif category == 'фрукты':
        await message.answer('Уточни, какие фрукты ты хочешь', reply_markup=keyboard)
    await OrderFood.waiting_for_food_name.set()


# step 3
@dp.message_handler(state=OrderFood.waiting_for_food_name, content_types=types.ContentTypes.TEXT)
async def food_step_3(message: types.Message, state: FSMContext):
    current_data = await state.get_data()
    category = current_data['chosen_food_category']
    name = message.text.lower()
    if name not in AVAILABLE_FOOD_CATEGORIES.get(category):
        await message.reply('Пожалуйста, не неси херню, используй клавиатуру ниже')
        return
    await state.update_data(chosen_food=name)
    await message.answer(text=HELP_TEXT_FOOD, reply_markup=types.ReplyKeyboardRemove())
    await OrderFood.waiting_for_other.set()


# step 4
@dp.message_handler(state=OrderFood.waiting_for_other, content_types=types.ContentTypes.TEXT)
async def food_step_4(message: types.Message, state=FSMContext):
    if not message.text.lower() == '/skip':
        await state.update_data(other=message.text.lower())
    await message.answer('Укажи количество')
    await OrderFood.waiting_for_amount.set()


# step 5
@dp.message_handler(state=OrderFood.waiting_for_amount, content_types=types.ContentTypes.TEXT)
async def food_step_5(message: types.Message, state=FSMContext):
    for unit in AVAILABLE_FOOD_MEASUREMENT_UNITS:
        if re.search(unit, message.text.lower()):
            break
    else:
        await message.answer(CHECK_TEXT)
    await state.update_data(amount=message.text.lower(), name=message.from_user.full_name)
    await message.answer(FINAL_TEXT)
    await state.finish()
