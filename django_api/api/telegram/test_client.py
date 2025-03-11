from unittest.mock import MagicMock, patch

import pytest
from telegram.client import TelegramClient


@pytest.fixture
def mock_bot():
    with patch("telegram.client.TeleBot") as MockBot:
        yield MockBot


@pytest.fixture
def telegram_client(mock_bot):
    client = TelegramClient("test_bot_token")
    client.bot = mock_bot()
    return client


def test_send_message(mock_bot, telegram_client):
    chat_id = 123456789
    text = "Hello, this is a test message."

    mock_bot.return_value.send_message = MagicMock()
    telegram_client.send_message(chat_id, text)
    mock_bot.return_value.send_message.assert_called_once_with(chat_id, text)


def test_close(mock_bot, telegram_client):
    telegram_client.close()
    mock_bot.return_value.stop_bot.assert_called_once()


if __name__ == "__main__":
    pytest.main()
