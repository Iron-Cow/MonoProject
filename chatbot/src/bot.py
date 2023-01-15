import os
import time
import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from loguru import logger
from config import config
from request_manager import RequestManager
from keyboard_manager import KeyboardManager
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode

kbm = KeyboardManager()



import sys
# from dotenv import load_dotenv
# from google.api_core.exceptions import AlreadyExists

# logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
logger.add("logs.log", rotation="1 week", format="{time} {level} {message}", level="INFO")



from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# from utils.bot_automation import confirmation_to_markup_option

# load_dotenv()
BOT_TOKEN = config.BOT_TOKEN
API_HOST = config.API_HOST
rm = RequestManager(API_HOST)
print(BOT_TOKEN)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

logger.info("Starting Bot")


# INFO COMMANDS
@dp.message_handler(state='*', commands=['start'])
async def start(message: types.Message):
    text = 'Hi, my young monouser.\nHere you can update your Monobank experience.\nTry /help to get more info'
    await bot.send_message(message.chat.id, text)

# INFO COMMANDS
@dp.message_handler(state='*', commands=['help'])
async def start(message: types.Message):

    # request user info
    text = 'Here is the list of available options:\n' \
           'Register \n'
    await bot.send_message(message.chat.id, text)


@dp.message_handler(state='*', commands=['hello'])
async def start(message: types.Message):
    text = 'Test start'
    await bot.send_message(message.chat.id, text)

# # -- INFO COMMANDS

# # +++ MONOBANK Block

# # STANDARD COMMANDS

@dp.message_handler()
async def echo(message: types.Message):
    logging.info(f'Received a message with no handling scenario from {message.from_user}. Echo!')
    rm.get("/", message)
    kb = kbm.get_inline_keyboard().row(kbm.register_button, kbm.cancel_button)
    await bot.send_message(message.chat.id, message.text, reply_markup=kb)

    # TODO HANDLE BUTTONS

async def reply_on_button(callback_query: types.CallbackQuery, button: InlineKeyboardButton, bot: Bot):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, text('picked:\n', code(f'{button.text}')),
                           parse_mode=ParseMode.MARKDOWN)
    await callback_query.message.delete_reply_markup()

@dp.callback_query_handler(lambda c: c.data == 'register_monouser')
async def register(callback_query: types.CallbackQuery):
    await reply_on_button(callback_query, kbm.register_button, bot)




async def on_startup(dp: Dispatcher):
    # global driver
    pass


#  -- STANDARD COMMANDS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_polling(dispatcher=dp, on_startup=on_startup)
