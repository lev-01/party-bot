from aiogram import executor
from launch import dp
import handlers
import database

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
