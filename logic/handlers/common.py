from logic import dp
from aiogram import types, filters
from aiogram.dispatcher import FSMContext
from logic.texts import START_TEXT
from logic.database.models import User, Category
from logic.database import Session
from sqlalchemy.sql import func
from sqlalchemy import select, insert, union, func

def check_if_user_exists(message: types.Message):
    with Session.begin() as session:
        user = session.execute(select(User).where(User.id == message.from_user.id)).all()
        if not user:
            session.add(User(id=message.from_user.id, first_name=message.from_user.first_name, last_name=message.from_user.last_name))


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    check_if_user_exists(message)
    await message.answer(START_TEXT)

# # step 1
# @dp.message_handler(commands='list', state='*')
# async def show_list(message: types.Message, state: FSMContext):
#     check_if_user_exists(message)
#     with Session.begin() as session:
#         u = union(
#             select(
#                 User.id.label('user_id'),
#                 Food.id.label('native_id'),
#                 Food.chosen_food.label('choice'),
#                 Food.amount,
#                 Food.other
#             ).join(Food),
#             select(
#                 User.id.label('user_id'),
#                 Alcohol.id.label('native_id'),
#                 Alcohol.chosen_alcohol.label('choice'),
#                 Alcohol.amount,
#                 Alcohol.other
#             ).join(Alcohol)
#         ).cte()

#         res = []
#         for row in session.execute(select(func.row_number().over(order_by=u.c.choice).label('row_number'), u).where(u.c.user_id==message.from_user.id)):
#             res.append(dict(row))
#             update_data = {f"/del{dict(row).get('row_number')}": dict(row)}
#             await state.update_data(update_data)
#         await message.answer('Список твоих пожеланий:\n' + '\n'.join(
#             [f"{elem.get('row_number')}. {elem.get('choice')}\nколичество: {elem.get('amount')}\nподробности: {elem.get('other', None)}\nудалить пожелание - /del{elem.get('row_number')}" for elem in res]
#         ))

#     # if len(res_list) == 0:
#     #     await message.answer('Список твоих пожеланий пока пуст.\nДобавить пожелание по еде - /food\nДобавить пожелание по алкоголю - /alcohol')
#     #     return
#     # await state.update_data(res=res)


# # step 2
# @dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[r'del(\d)+']))
# async def delete_item(message: types.Message, state: FSMContext):
#     user_data = await state.get_data()
#     with Session.begin() as session:
#         session.delete(user_data[message.text])
#     print(message.text)
#     print(user_data)
#     await message.answer('Пожелание удалено.')
#     await state.finish()
