from aiogram import executor
from logic import dp, handlers, database

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
