import logging
import os
import sys
from datetime import datetime

from loguru import logger
from telegram.client import TelegramClient

logger.remove()
logger.level("INFO", color="<blue>", icon="!!!")
logger.add(
    sys.stderr,
    format="<level>{time:[DD/MMM/YYYY HH:mm:ss]} | {level} | {message}</level>",
    colorize=True,
    diagnose=True,
    level="INFO",
)


# TODO: add later after docker no access fix
# logger.add(
#     "logs/logs.log",
#     format="<level>{time:[DD/MMM/YYYY HH:mm:ss]} | {level} | {message}</level>",
#     rotation="100 MB",
# )


class LoguruHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.telegram_bot = TelegramClient(os.environ.get("LOGS_BOT_TOKEN", "not set"))
        self.telegram_logs_chat_id = int(os.environ.get("ADMIN_TG_ID", -1))
        self.env = os.environ.get("ENV", "not set")

    """Custom Loguru handler that integrates with Python's logging module"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = {
                logging.CRITICAL: "CRITICAL",
                logging.ERROR: "ERROR",
                logging.WARNING: "WARNING",
                logging.INFO: "INFO",
                logging.DEBUG: "DEBUG",
                logging.NOTSET: "NOTSET",
            }.get(record.levelno, "INFO")

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        # Log message
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

        # 🔥 Send critical errors to Telegram
        if level in ["ERROR", "CRITICAL"] and self.telegram_bot:
            try:
                error_message = (
                    f"🚨 *Error Alert*\n"
                    f"🕒 {datetime.now().strftime('%d/%b/%Y %H:%M:%S')}\n"
                    f"🌐 Environment: {self.env}\n"
                    f"🔴 Level: {level}\n"
                    f"📄 Message: {record.getMessage()}"
                )
                self.telegram_bot.send_message(
                    self.telegram_logs_chat_id, error_message
                )
                logger.info("Sent Telegram alert for ERROR.")
            except Exception as e:
                logger.error(f"Failed to send Telegram alert: {e}")


# Attach the custom handler to Python’s logging module
logging.basicConfig(handlers=[LoguruHandler()], level=logging.INFO)

# Example usage
if __name__ == "__main__":
    logger.info("This is an informational message.")
    logger.error("This is an error message that will be sent to Telegram!")
