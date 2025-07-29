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

    def send_message(
        self, chat_id: int | str, text: str, parse_mode: str | None = None
    ):
        """
        Send a message to a chat.

        Args:
            chat_id: The chat ID to send the message to
            text: The message text
            parse_mode: Optional parse mode ('HTML', 'Markdown', 'MarkdownV2')
        """
        self.bot.send_message(chat_id, text, parse_mode=parse_mode)

    def send_html_message(self, chat_id: int | str, text: str):
        """
        Send an HTML-formatted message to a chat.

        Args:
            chat_id: The chat ID to send the message to
            text: The HTML-formatted message text

            text supported examples:
            <b>Bold text</b>
            <i>Italic text</i>
            <u>Underlined text</u>
            <code>Monospace text</code>
            <a href="https://example.com">Link</a>
            <b>List Examples:</b>
            • <i>Bullet point 1</i>
            • <i>Bullet point 2</i>
            • <i>Bullet point 3</i>
            <b>Numbered List:</b>
            1️⃣ <code>First item</code>
            2️⃣ <code>Second item</code>
            3️⃣ <code>Third item</code>

        """
        self.bot.send_message(chat_id, text, parse_mode="HTML")

    def close(self):
        self.bot.stop_bot()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    client1 = TelegramClient(os.environ.get("LOGS_BOT_TOKEN", "not set bot token"))

    # Example of sending a regular message
    client1.send_message(
        os.environ.get("ADMIN_TG_ID", "not set tg_id"), "Hello, this is a test message."
    )

    # Example of sending an HTML-formatted message
    html_message = """
<b>Bold text</b>
<i>Italic text</i>
<u>Underlined text</u>
<code>Monospace text</code>
<a href="https://example.com">Link</a>

<b>List Examples:</b>
• <i>Bullet point 1</i>
• <i>Bullet point 2</i>
• <i>Bullet point 3</i>

<b>Numbered List:</b>
1️⃣ <code>First item</code>
2️⃣ <code>Second item</code>
3️⃣ <code>Third item</code>

<b>Checklist:</b>
☑️ <i>Completed task</i>
☐ <i>Pending task</i>
☐ <i>Another pending task</i>
"""
    client1.send_html_message(
        os.environ.get("ADMIN_TG_ID", "not set tg_id"), html_message
    )
