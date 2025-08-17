# pyright: reportArgumentType = false

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardManager:
    def __init__(self):
        # self.button_cancel = KeyboardButton('/cancel 🤨')
        # self.button_start = KeyboardButton('/start 🥳')
        # self.button_help = KeyboardButton('/help 🤔')
        # self.button_reg = KeyboardButton('/register 🤓')
        self.mono_operations_button = InlineKeyboardButton(
            "Check my cards", callback_data="mono_cards_summary"
        )
        self.add_mono_token_button = InlineKeyboardButton(
            "Register Monotoken", callback_data="add_mono_token"
        )
        self.change_mono_token_button = InlineKeyboardButton(
            "Change mono token", callback_data="change_mono_token"
        )
        self.delete_mono_token_button = InlineKeyboardButton(
            "Delete mono token", callback_data="delete_mono_token_warning"
        )
        self.register_button = InlineKeyboardButton(
            "Register Monouser", callback_data="register_monouser"
        )
        self.cancel_button = InlineKeyboardButton("Cancel", callback_data="cancel")
        self.get_mono_token_button = InlineKeyboardButton(
            "Get MonoToken", url="https://api.monobank.ua/"
        )
        self.get_mono_jars = InlineKeyboardButton(
            "Get my jars", callback_data="get_user_jars"
        )
        self.get_mono_jars_budget = InlineKeyboardButton(
            "Get my budget jars", callback_data="get_user_jars_budget"
        )
        # Dynamic buttons: created on the fly with callbacks

    @staticmethod
    def get_inline_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup()
