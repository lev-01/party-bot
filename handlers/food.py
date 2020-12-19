from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from launch import dp
from database import session, Food, User
from texts import AVAILABLE_FOOD_CATEGORIES, HELP_TEXT_FOOD, CHECK_TEXT, AVAILABLE_FOOD_MEASUREMENT_UNITS, FINAL_TEXT
from general import check_if_user_exists
import re


class OrderFood(StatesGroup):
    waiting_for_food_category = State()
    waiting_for_food_name = State()
    waiting_for_other = State()
    waiting_for_amount = State()


# step 1
@dp.message_handler(commands='food', state='*')
async def food_step_1(message: types.Message):
    check_if_user_exists(message)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in sorted(AVAILABLE_FOOD_CATEGORIES):
        keyboard.add(category)
    await message.answer('Выбери категорию еды', reply_markup=keyboard)
    await OrderFood.waiting_for_food_category.set()


# step 2
@dp.message_handler(state=OrderFood.waiting_for_food_category, content_types=types.ContentTypes.TEXT)
async def food_step_2(message: types.Message, state: FSMContext):
    check_if_user_exists(message)
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await OrderFood.waiting_for_food_category.set()
        return
    category = message.text.lower()
    if category not in AVAILABLE_FOOD_CATEGORIES:
        await message.reply('Пожалуйста, не неси херню, используй клавиатуру ниже')
        return
    await state.update_data(chosen_food_category=category)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in sorted(AVAILABLE_FOOD_CATEGORIES.get(category)):
        keyboard.add(name)
    await message.answer('Уточни, что именно ты хочешь', reply_markup=keyboard)
    await OrderFood.waiting_for_food_name.set()


# step 3
@dp.message_handler(state=OrderFood.waiting_for_food_name, content_types=types.ContentTypes.TEXT)
async def food_step_3(message: types.Message, state: FSMContext):
    check_if_user_exists(message)
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await OrderFood.waiting_for_food_name.set()
        return
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
    check_if_user_exists(message)
    if message.text.lower() in ('/list', '/alcohol'):
        await message.answer('Сначала закончи вносить пожелание, потом сможешь посмотреть список или внести новое пожелание.')
        await OrderFood.waiting_for_other.set()
        return
    if not message.text.lower() == '/skip':
        try:
            assert len(message.text) <= 250
        except AssertionError:
            await message.answer(f'У тебя какие-то слишком подробные подробности.\n'
                                 f'Количество символов - {len(message.text)}.\n'
                                 f'Попробуй еще раз, только теперь уместись в 250 символов.')
            await OrderFood.waiting_for_other.set()
            return
        else:
            await state.update_data(other=message.text.lower())
    await message.answer('Укажи количество')
    await OrderFood.waiting_for_amount.set()


# step 5
@dp.message_handler(state=OrderFood.waiting_for_amount, content_types=types.ContentTypes.TEXT)
async def food_step_5(message: types.Message, state=FSMContext):
    check_if_user_exists(message)
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await OrderFood.waiting_for_amount.set()
        return
    for unit in AVAILABLE_FOOD_MEASUREMENT_UNITS:
        if re.search(unit, message.text.lower()):
            break
    else:
        await message.answer(CHECK_TEXT)
        await OrderFood.waiting_for_amount.set()
        return
    await state.update_data(amount=message.text.lower())

    user_data = await state.get_data()

    food = Food(user_id=message.from_user.id,
                chosen_food=user_data['chosen_food'],
                amount=user_data['amount'],
                other=user_data['other']) if 'other' in user_data.keys() else Food(user_id=message.from_user.id,
                                                                                   chosen_food=user_data['chosen_food'],
                                                                                   amount=user_data['amount'])
    session.add(food)
    session.commit()

    await message.answer(FINAL_TEXT)
    await state.finish()
