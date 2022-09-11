import os
import time
import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import requests
# from dotenv import load_dotenv
# from google.api_core.exceptions import AlreadyExists


from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# from utils.bot_automation import confirmation_to_markup_option

# load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "NOT_SET")
print(BOT_TOKEN)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


# INFO COMMANDS
@dp.message_handler(state='*', commands=['start'])
async def start(message: types.Message):
    text = 'Hi, my young monouser.\nHere you can update your Monobank experience.\nTry /help to get more info'
    await bot.send_message(message.chat.id, text)


# # -- INFO COMMANDS

# # +++ MONOBANK Block

# # STANDARD COMMANDS

@dp.message_handler()
async def echo(message: types.Message):
    logging.info(f'Received a message with no handling scenario from {message.from_user}. Echo!')
    requests.get("http://api:8000")
    await bot.send_message(message.chat.id, message.text)


async def on_startup(dp: Dispatcher):
    # global driver
    pass


#  -- STANDARD COMMANDS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_polling(dispatcher=dp, on_startup=on_startup)
