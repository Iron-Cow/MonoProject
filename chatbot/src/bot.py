# pyright: reportInvalidStringEscapeSequence = false
# pyright: reportArgumentType = false

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
from utils import generate_password, get_jar_data

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
    has_user = False
    has_account = False
    available_commands = """
    /help - check available options
    """
    resp = rm.get(f"/monobank/monoaccounts/")
    if resp.status_code != 200:
        text = f"something went wrong try again or contast the support"
        await bot.send_message(message.chat.id, text)

    # [{
    #     "user": "552901111",
    #     "mono_token": "umedfPsJgqMZP5pHeFcy8Y6skmSJsadfasdfsadfasd",
    #     "active": true
    # }]
    for user in resp.json():
        if user.get("user") == str(message.from_user.id):
            has_account = True
            break
    else:
        available_commands += "\n /register - register your account"

    if has_account:
        available_commands += "\n /monojars - get you jars "

    await bot.send_message(message.chat.id, available_commands)


@dp.message_handler(state="*", commands=["monojars"])
async def monojars(message: types.Message):
    kb = (
        kbm.get_inline_keyboard()
        .row(kbm.get_mono_jars)
        .row(kbm.get_mono_jars_budget)
        .row(kbm.cancel_button)
    )
    await bot.send_message(
        message.chat.id,
        "pick your option",
        reply_markup=kb,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.callback_query_handler(
    lambda c: c.data in ["get_user_jars", "get_user_jars_budget"]
)
async def get_user_jars_combined(callback_query: types.CallbackQuery):
    is_budget = callback_query.data == "get_user_jars_budget"
    button = kbm.get_mono_jars_budget if is_budget else kbm.get_mono_jars
    await reply_on_button(callback_query, button, bot)
    url = f"/monobank/monojars/?users={callback_query.from_user.id}"
    if is_budget:
        url += "&is_budget=True&with_family=True"
    resp = rm.get(url)
    if resp.status_code != 200:
        txt = "Something went wrong. Try other commands or /help"
        await bot.send_message(callback_query.message.chat.id, txt)
        return

    data = resp.json()
    if len(data) == 0:
        txt = "No budget jars to display" if is_budget else "No jars to display"
        await bot.send_message(callback_query.message.chat.id, txt)
        return

    for jar in data:
        jar_obj = get_jar_data(jar)
        title = f"**__{jar_obj.title}__**"
        value = f"*{jar_obj.currency.flag} {jar_obj.balance / 100}{jar_obj.currency.name}*\n\[{jar_obj.owner_name}\]"
        # Toggle budget button reflects current state
        current_flag = 1 if getattr(jar_obj, "is_budget", False) else 0
        button_text = "Unset budget" if current_flag == 1 else "Set as budget"
        toggle_button = InlineKeyboardButton(
            button_text,
            callback_data=f"toggle_budget_{jar_obj.id}*{current_flag}",
        )
        months_button = InlineKeyboardButton(
            "📅 Available months", callback_data=f"jar_months_{jar_obj.id}"
        )
        kb = kbm.get_inline_keyboard().row(toggle_button, months_button)
        await bot.send_message(
            callback_query.message.chat.id,
            f"{title}\n{value}".replace(".", "\\."),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=kb,
        )


@dp.callback_query_handler(lambda c: c.data.startswith("jar_months_"))
async def jar_available_months_handler(callback_query: types.CallbackQuery):
    jar_id = callback_query.data.replace("jar_months_", "")
    # Fetch jar details for title and currency
    jar_resp = rm.get(f"/monobank/monojars/{jar_id}/")
    months_resp = rm.get(f"/monobank/monojars/{jar_id}/available-months/")

    if jar_resp.status_code != 200 or months_resp.status_code != 200:
        await bot.send_message(
            callback_query.message.chat.id,
            "Failed to fetch available months. Please try again later.",
        )
        return

    jar = jar_resp.json()
    jar_obj = get_jar_data(jar)
    months = months_resp.json()  # ["YYYY-MM-01", ...]

    if len(months) == 0:
        await bot.send_message(
            callback_query.message.chat.id,
            f"No transactions months for {jar_obj.title}".replace(".", "\\."),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    kb = kbm.get_inline_keyboard()
    # Add month buttons (show as YYYY-MM)
    for month_str in months:
        label = f"{month_str[:7]}"
        kb = kb.add(
            InlineKeyboardButton(
                f"📆 {label}",
                callback_data=f"jar_month_summary_{jar_obj.id}*{month_str}",
            )
        )

    header = f"**__{jar_obj.title}__**\nPick month:".replace(".", "\\.")
    await bot.send_message(
        callback_query.message.chat.id,
        header,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda c: c.data.startswith("jar_month_summary_"))
async def jar_month_summary_handler(callback_query: types.CallbackQuery):
    payload = callback_query.data.replace("jar_month_summary_", "")
    jar_id, month_str = payload.split("*")

    # Fetch summary and jar details for formatting
    summary_resp = rm.get(
        f"/monobank/monojars/{jar_id}/month-summary/?month={month_str}"
    )
    jar_resp = rm.get(f"/monobank/monojars/{jar_id}/")

    if summary_resp.status_code != 200 or jar_resp.status_code != 200:
        await bot.send_message(
            callback_query.message.chat.id,
            "Failed to fetch month summary. Please try again later.",
        )
        return

    summary = summary_resp.json()
    jar = jar_resp.json()
    jar_obj = get_jar_data(jar)

    def fmt(amount: int) -> str:
        try:
            return f"{(amount or 0) / 100:.2f}"
        except Exception:
            return "0.00"

    start_balance = fmt(summary.get("start_balance", 0))
    budget = fmt(summary.get("budget", 0))
    end_balance = fmt(summary.get("end_balance", 0))
    spent = fmt(summary.get("spent", 0))

    text_msg = (
        f"📦 Jar: {jar_obj.title}\n"
        f"📅 Month: {month_str[:7]}\n"
        f"🔹 Start balance: 💰 {start_balance} {jar_obj.currency.name}\n"
        f"📈 Budget (max deposit): ➕ {budget} {jar_obj.currency.name}\n"
        f"🔻 End balance: 💰 {end_balance} {jar_obj.currency.name}\n"
        f"🧮 Spent: {spent} {jar_obj.currency.name}"
    )

    await bot.send_message(
        callback_query.message.chat.id,
        text_msg,
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.callback_query_handler(lambda c: c.data.startswith("toggle_budget_"))
async def toggle_budget_handler(callback_query: types.CallbackQuery):
    jar_id = callback_query.data.replace("toggle_budget_", "").split("*")[0]
    current_flag = int(callback_query.data.replace("toggle_budget_", "").split("*")[1])
    new_flag = 1 - current_flag

    # Call API to set this jar as budget for the user
    resp = rm.patch(
        f"/monobank/monojars/{jar_id}/set_budget_status/", {"is_budget": bool(new_flag)}
    )

    if resp.status_code == 200:
        # Update the inline keyboard in place with the opposite action
        next_text = "Unset budget" if new_flag == 1 else "Set as budget"
        new_button = InlineKeyboardButton(
            next_text,
            callback_data=f"toggle_budget_{jar_id}*{new_flag}",
        )
        new_kb = kbm.get_inline_keyboard().add(new_button)
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=new_kb,
        )
        await bot.answer_callback_query(
            callback_query.id,
            text=("Set as budget ✅" if new_flag == 1 else "Unset budget ✅"),
            show_alert=False,
        )
    else:
        await bot.answer_callback_query(
            callback_query.id,
            text=f"Failed to toggle budget: {resp.status_code}",
            show_alert=True,
        )


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
async def token_add(message: types.Message):
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
async def hello(message: types.Message):
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
async def register_monouser(callback_query: types.CallbackQuery):
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
async def cancel(callback_query: types.CallbackQuery):
    await reply_on_button(callback_query, kbm.cancel_button, bot)
    state = dp.current_state(user=callback_query.from_user.id)
    await state.reset_state()


async def on_startup(_: Dispatcher):
    # global driver
    pass


#  -- STANDARD COMMANDS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_polling(dispatcher=dp, on_startup=on_startup)
