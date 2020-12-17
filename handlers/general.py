from launch import dp
from aiogram import types, filters
from aiogram.dispatcher import FSMContext
from texts import START_TEXT
from database import session, User, Food, Alcohol
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer(START_TEXT)
    user = User(id=message.from_user.id,
                name=message.from_user.full_name)
    try:
        session.query(User).filter(User.id == message.from_user.id, User.name == message.from_user.full_name).one()
    except NoResultFound:
        session.add(user)
        session.commit()


# step 1
@dp.message_handler(commands='list', state='*')
async def show_list(message: types.Message, state: FSMContext):
    query = '''
        with t as (
        select "user".id user_id, food.id native_id, food.chosen_food choice, food.amount, food.other
        from "user"
        JOIN food ON food.user_id = "user".id
        UNION
        select "user".id user_id, alcohol.id native_id, alcohol.chosen_alcohol choice, alcohol.amount, alcohol.other
        from "user"
        JOIN alcohol ON alcohol.user_id = "user".id
    )
    select row_number() over (order by choice), * from t where user_id=:id'''

    res_dict, res_list = {}, []
    for row in session.execute(query, {'id': message.from_user.id}):
        for column, value in row.items():
            res_dict = {**res_dict, **{column: value}}
        res_list.append(res_dict)

    if len(res_list) == 0:
        await message.answer('Список твоих пожеланий пока пуст.\n'
                             'Добавить пожелание по еде - /food\n'
                             'Добавить пожелание по алкоголю - /alcohol')
        return

    text, res = [], {}
    for row in res_list:
        row_number, _, native_id, choice, amount, other = row.values()
        if other is not None:
            text.append(f'{row_number}. {choice}\n'
                        f'количество: {amount}\n'
                        f'подробности: {other}\n'
                        f'удалить пожелание - /del{row_number}')
        else:
            text.append(f'{row_number}. {choice}\n'
                        f'количество: {amount}\n'
                        f'удалить пожелание - /del{row_number}')
        res[text[-1][-5:]] = native_id
    await message.answer('Список твоих пожеланий:\n' + '\n'.join(text))
    await state.update_data(res=res)


# step 2
@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[r'del(\d)+']))
async def delete_item(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        session.query(Alcohol).filter(Alcohol.user_id == message.from_user.id,
                                      Alcohol.id == user_data['res'][message.text]).one()
        session.query(Alcohol).filter(Alcohol.id == user_data['res'][message.text]).delete()
    except NoResultFound:
        session.query(Food).filter(Food.id == user_data['res'][message.text]).delete()
    session.commit()
    await message.answer('Пожелание удалено.')
    await state.finish()
