import logging

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils.executor import start_polling
from aiogram.utils.markdown import code, text
from config import get_config
from keyboard_manager import KeyboardManager
from loguru import logger
from request_manager import RequestManager
from states import MonotokenStates
from utils import generate_password

PASSWORD_LENGTH = 16

kbm = KeyboardManager()

# logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
logger.add(
    "logs.log", rotation="1 week", format="{time} {level} {message}", level="INFO"
)

from aiogram.types import InlineKeyboardButton

# load_dotenv()
config = get_config()
rm = RequestManager(config)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

logger.info("Starting Bot")


# INFO COMMANDS
@dp.message_handler(state="*", commands=["start"])
async def start(message: types.Message):
    text = "Hi, my young monouser.\nHere you can update your Monobank experience.\nTry /help to get more info or click /register to start"
    await bot.send_message(message.chat.id, text)


@dp.message_handler(state="*", commands=["help"])
async def help(message: types.Message):
    text = "help handler"
    await bot.send_message(message.chat.id, text)


# INFO COMMANDS
@dp.message_handler(state="*", commands=["register"])
async def register(message: types.Message):
    resp = rm.get(f"/account/users/{message.from_user.id}")
    if resp.status_code == 200:
        txt = "Looks like you are registered already. Try other commands or /help"
        await bot.send_message(message.chat.id, txt)
        return
    resp = text(
        "This button will create account with your telegram ID and name \+ generated password for access website\. "
        "Click here to start using MonoHelper"
    )
    kb = kbm.get_inline_keyboard().row(kbm.register_button, kbm.cancel_button)
    await bot.send_message(
        message.chat.id, resp, reply_markup=kb, parse_mode=ParseMode.MARKDOWN_V2
    )


@dp.message_handler(state="*", commands=["token_add"])
async def register(message: types.Message):
    # TODO: check if exists
    resp = text(
        "Follow the link to get monobank token\. Please copy it and come back to insert it\. \n"
        "Note: this token give read\-only permissions and can be revoked anytime by same link\. Surely, "
        "revoked token will let you use this service untill you replace it with valid one\."
    )
    kb = kbm.get_inline_keyboard().row(
        kbm.get_mono_token_button, kbm.add_mono_token_button, kbm.cancel_button
    )
    await bot.send_message(
        message.chat.id, resp, reply_markup=kb, parse_mode=ParseMode.MARKDOWN_V2
    )


@dp.message_handler(state="*", commands=["hello"])
async def start(message: types.Message):
    text = "Test start"
    await bot.send_message(message.chat.id, text)


# # -- INFO COMMANDS

# # +++ MONOBANK Block

# # STANDARD COMMANDS


@dp.message_handler()
async def echo(message: types.Message):
    logging.info(
        f"Received a message with no handling scenario from {message.from_user}. Echo!"
    )
    await bot.send_message(
        message.chat.id,
        text("Something unknown:\n", code(message.text)),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    # TODO HANDLE BUTTONS


async def reply_on_button(
    callback_query: types.CallbackQuery, button: InlineKeyboardButton, bot: Bot
):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        text("picked:\n", code(f"{button.text}")),
        parse_mode=ParseMode.MARKDOWN,
    )
    await callback_query.message.delete_reply_markup()


@dp.callback_query_handler(lambda c: c.data == "register_monouser")
async def register(callback_query: types.CallbackQuery):
    await reply_on_button(callback_query, kbm.register_button, bot)
    password = generate_password(PASSWORD_LENGTH)
    username = (
        f"{callback_query.from_user.last_name} {callback_query.from_user.first_name}"
    )
    resp = rm.post(
        "/account/users/",
        {
            "tg_id": f"{callback_query.from_user.id}",
            "password": password,
            "name": username,
        },
    )
    if resp.status_code != 201:
        await bot.send_message(
            callback_query.message.chat.id,
            text("Something went wrong:\n", code(resp.text)),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return
    response = f"||{password}||"
    await bot.send_message(
        callback_query.message.chat.id,
        text("login:\n", code(f"{callback_query.from_user.id}")),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await bot.send_message(
        callback_query.message.chat.id,
        text("name:\n", code(username)),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await bot.send_message(
        callback_query.message.chat.id,
        text("password:\n", text(f"||{password}||")),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    txt = "Now you can add mono token to access your accounts. Press /token_add to continue"
    await bot.send_message(callback_query.message.chat.id, txt)


@dp.callback_query_handler(lambda c: c.data == "add_mono_token")
async def add_monotoken(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    await state.set_state(state=MonotokenStates.token_enter)
    txt = "Send your token or cancel"
    await reply_on_button(callback_query, kbm.add_mono_token_button, bot)
    kb = kbm.get_inline_keyboard().row(kbm.cancel_button)
    await bot.send_message(
        callback_query.message.chat.id,
        txt,
        reply_markup=kb,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.message_handler(state=MonotokenStates.token_enter)
async def token(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()
    resp = rm.post(
        "/monobank/monoaccounts/",
        {"user": f"{message.from_user.id}", "mono_token": message.text},
    )
    if resp.status_code != 201:
        await bot.send_message(message.chat.id, resp.text)
        await bot.send_message(
            message.chat.id, "Something went wrong! Try whole process again /token_add"
        )
        return

    await bot.send_message(
        message.chat.id,
        "Great! Now you can use service to track your monobank operations. Try /help",
    )


@dp.callback_query_handler(lambda c: c.data == "cancel")
async def register(callback_query: types.CallbackQuery):
    await reply_on_button(callback_query, kbm.cancel_button, bot)
    state = dp.current_state(user=callback_query.from_user.id)
    await state.reset_state()


async def on_startup(dp: Dispatcher):
    # global driver
    pass


#  -- STANDARD COMMANDS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_polling(dispatcher=dp, on_startup=on_startup)
