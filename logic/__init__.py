import os
import logging
import logging.config
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(filename='./logs/bot.log', format='%(asctime)s | %(levelname)s | %(name)s | %(message)s', level=logging.INFO)

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())