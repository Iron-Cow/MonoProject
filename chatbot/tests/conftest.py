import asyncio

# Mock the aiogram Bot class before any imports to prevent token validation
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

# Create a proper Bot subclass that passes isinstance checks
from aiogram import Bot as OriginalBot


class MockBot(OriginalBot):
    def __init__(self, *args, **kwargs):
        # Skip parent __init__ to avoid token validation
        pass


# Patch aiogram.Bot globally for tests
aiogram_patch = patch("aiogram.Bot", MockBot)
aiogram_patch.start()


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        return self._json_data


class ApiServiceMock:
    def __init__(self):
        self.calls = []
        self._responses = {}

    def when(self, method: str, endpoint: str, response: DummyResponse):
        self._responses[(method.upper(), endpoint)] = response
        return self

    def _get_response(self, method: str, endpoint: str) -> DummyResponse:
        self.calls.append((method.upper(), endpoint))
        return self._responses.get(
            (method.upper(), endpoint), DummyResponse(404, None, "Not Found")
        )

    # Methods mimic RequestManager
    def get(self, endpoint: str):
        return self._get_response("GET", endpoint)

    def post(self, endpoint: str, body=None):
        return self._get_response("POST", endpoint)

    def patch(self, endpoint: str, body=None):
        return self._get_response("PATCH", endpoint)

    def delete(self, endpoint: str, body=None):
        return self._get_response("DELETE", endpoint)


@pytest.fixture
def mock_config(monkeypatch):
    """Mock the config to use valid test values"""
    from src import config as config_module

    class MockConfig:
        BOT_TOKEN = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"  # Valid token format
        API_HOST = "http://test-api"
        CHAT_BOT_API_KEY = "test_key"
        API_ADMIN_USERNAME = "test_user"
        API_ADMIN_PASSWORD = "test_pass"

    def mock_get_config():
        return MockConfig()

    monkeypatch.setattr(config_module, "get_config", mock_get_config)
    return MockConfig()


@pytest.fixture
def api_mock(mock_config, monkeypatch):
    from src import bot as bot_module

    mock = ApiServiceMock()
    # Replace RequestManager instance used in bot.py
    monkeypatch.setattr(bot_module, "rm", mock, raising=True)
    return mock


class SentMessage:
    def __init__(
        self,
        chat_id,
        text=None,
        reply_markup=None,
        parse_mode=None,
        photo=None,
        caption=None,
    ):
        self.chat_id = chat_id
        self.text = text
        self.reply_markup = reply_markup
        self.parse_mode = parse_mode
        self.photo = photo
        self.caption = caption


class BotStub:
    def __init__(self):
        self.sent = []
        self.answered_callbacks = []
        self.edited_markups = []

    async def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        self.sent.append(
            SentMessage(
                chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode
            )
        )
        return types.SimpleNamespace(
            message_id=len(self.sent), chat=types.SimpleNamespace(id=chat_id)
        )

    async def answer_callback_query(self, cb_id, text=None, show_alert=False):
        self.answered_callbacks.append((cb_id, text, show_alert))

    async def edit_message_reply_markup(self, chat_id, message_id, reply_markup=None):
        self.edited_markups.append((chat_id, message_id, reply_markup))

    async def send_photo(self, chat_id, photo, caption=None):
        self.sent.append(SentMessage(chat_id, photo=photo, caption=caption))


@pytest.fixture
def bot_stub(mock_config, monkeypatch):
    from src import bot as bot_module

    stub = BotStub()
    monkeypatch.setattr(bot_module, "bot", stub, raising=True)
    return stub


@pytest.fixture
def dp_module():
    # Provide access to the module so tests can call handlers directly
    from src import bot as bot_module

    return bot_module


@pytest.fixture
def event_loop():
    # pytest-asyncio style loop, but we avoid adding dependency and keep simple
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
