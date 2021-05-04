from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from logic import dp
from logic.database import Session
from logic.database.models import Item, Category
from logic.texts import AVAILABLE_FOOD_CATEGORIES, HELP_TEXT_FOOD, CHECK_TEXT, AVAILABLE_FOOD_MEASUREMENT_UNITS, FINAL_TEXT
from sqlalchemy import select
from .common import check_if_user_exists
import re


class Order(StatesGroup):
    waiting_for_category = State()
    waiting_for_name = State()
    waiting_for_other = State()
    waiting_for_amount = State()


# step 1
@dp.message_handler(commands='add', state='*')
async def food_step_1(message: types.Message):
    check_if_user_exists(message)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    with Session.begin() as session:
        categories = session.execute(select(Category.name).where(Category.parent_id==None)).scalars().all()
    for category in sorted(categories):
        keyboard.add(category)
    await message.answer('Выбери категорию', reply_markup=keyboard)
    await Order.waiting_for_category.set()


# step 2
@dp.message_handler(state=Order.waiting_for_category, content_types=types.ContentTypes.TEXT)
async def food_step_2(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await Order.waiting_for_category.set()
        return

    with Session.begin() as session:
        stmt = select(Category.id).where(Category.name)==message.text.lower()
        category_id = session.execute(stmt).scalars().one()
        categories = session.execute(select(Category.name).where(Category.parent_id==stmt)).scalars().all()

    for name in sorted(categories):
        keyboard.add(name)

    await state.update_data(category_id=category_id)
    await message.answer('Уточни, что именно ты хочешь', reply_markup=keyboard)
    await Order.waiting_for_name.set()


# step 3
@dp.message_handler(state=Order.waiting_for_name, content_types=types.ContentTypes.TEXT)
async def food_step_3(message: types.Message, state: FSMContext):
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await Order.waiting_for_name.set()
        return

    current_data = await state.get_data()
    print(current_data)
    category = current_data.get('chosen_category')

    await state.update_data(choice=message.text.lower())
    await message.answer(text=HELP_TEXT_FOOD, reply_markup=types.ReplyKeyboardRemove())
    await Order.waiting_for_other.set()


# step 4
@dp.message_handler(state=Order.waiting_for_other, content_types=types.ContentTypes.TEXT)
async def food_step_4(message: types.Message, state=FSMContext):
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
            await Order.waiting_for_other.set()
            return
        else:
            await state.update_data(other=message.text.lower())
    await message.answer('Укажи количество')
    await Order.waiting_for_amount.set()


# step 5
@dp.message_handler(state=Order.waiting_for_amount, content_types=types.ContentTypes.TEXT)
async def food_step_5(message: types.Message, state=FSMContext):
    if message.text.lower() == '/list':
        await message.answer('Сначала закончи вносить пожелание, потом посмотришь список.')
        await Order.waiting_for_amount.set()
        return

    for unit in AVAILABLE_FOOD_MEASUREMENT_UNITS:
        if re.search(unit, message.text.lower()):
            break
    else:
        await message.answer(CHECK_TEXT)
        await Order.waiting_for_amount.set()
        return
    await state.update_data(amount=message.text.lower())

    user_data = await state.get_data()
    with Session.begin() as session:
        item = Item(user_id=message.from_user.id,
                    chosen_food=user_data['chosen_food'],
                    amount=user_data['amount'],
                    other=user_data['other'] if 'other' in user_data.keys() else None)
        session.add(item)

    await message.answer(FINAL_TEXT)
    await state.finish()
