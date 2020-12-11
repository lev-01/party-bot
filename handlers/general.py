from launch import dp
from aiogram import types
from texts import START_TEXT


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
   await message.answer(START_TEXT)
