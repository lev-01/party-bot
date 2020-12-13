from launch import dp
from database import db
from aiogram import types, filters
from aiogram.dispatcher import FSMContext
from texts import START_TEXT


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer(START_TEXT)


# step 1
@dp.message_handler(commands='list', state='*')
async def show_list(message: types.Message, state: FSMContext):
    lst = await db.get_list(message.from_user.full_name)
    if len(lst) == 0:
        await message.answer('Список твоих пожеланий пока пуст.\n'
                             'Добавить пожелание по еде - /food\n'
                             'Добавить пожелание по алкоголю - /alcohol')
        return
    text, res = [], {}
    for row in lst:
        item_id, native_id, item_name, item_amount, item_other = row
        if item_other is not None:
            text.append(f'{item_id}. {item_name}\n'
                        f'количество: {item_amount}\n'
                        f'подробности: {item_other}\n'
                        f'удалить пожелание - /del{item_id}')
        else:
            text.append(f'{item_id}. {item_name}\n'
                        f'количество: {item_amount}\n'
                        f'удалить пожелание - /del{item_id}')
        res[text[-1][-5:]] = native_id, item_name
    await message.answer('Список твоих пожеланий:\n' + '\n'.join(text))
    await state.update_data(res=res)


# step 2
@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['del(\d)+']))
async def delete_item(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data['res'][message.text] in [tuple(item.values()) for item in
                                          db.fetchall('alcohol', columns=['id', 'chosen_alcohol'])]:
        db.delete('alcohol', user_data['res'][message.text][0])
    else:
        db.delete('food', user_data['res'][message.text][0])
    await message.answer('Пожелание удалено.')
    await state.finish()
