import os

from telebot import TeleBot


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class TelegramClient(metaclass=SingletonMeta):
    def __init__(self, bot_token: str):
        self.token = bot_token
        self.bot = TeleBot(token=bot_token)

    def send_message(self, chat_id: int, text: str):
        self.bot.send_message(chat_id, text)

    def close(self):
        self.bot.stop_bot()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    client1 = TelegramClient(os.environ.get("LOGS_BOT_TOKEN"))
    client1.send_message(
        os.environ.get("ADMIN_TG_ID"), "Hello, this is a test message."
    )
