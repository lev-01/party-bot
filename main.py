from aiogram import executor
from logic import dp

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
