import requests
from aiogram import types
from config import config


class RequestManager:
    def __init__(self, api_host: str):
        self.api_host = api_host
        self.CHAT_BOT_API_KEY = config.CHAT_BOT_API_KEY

    def create_default_headers(self, tg_id: str) -> dict:
        return {"CHAT_BOT_API_KEY": self.CHAT_BOT_API_KEY, "tg_id": f"{tg_id}"}

    def get(self, endpoint: str, message: types.Message | types.CallbackQuery, api_host: str | None = None):
        tg_id = message.from_user.id
        API_HOST = api_host or self.api_host
        if endpoint[0] != "/":
            endpoint = "/" + endpoint

        headers = self.create_default_headers(tg_id)
        requests.get(f"{API_HOST}{endpoint}", headers=headers)
