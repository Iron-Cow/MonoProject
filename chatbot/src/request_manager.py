import requests
from aiogram import types

class RequestManager:
    def __init__(self, api_host: str):
        self.api_host = api_host

    def get(self, endpoint: str, message: types.Message | types.CallbackQuery, api_host: str | None):
        tg_id = message.from_user.id
        API_HOST = api_host or self.api_host
        