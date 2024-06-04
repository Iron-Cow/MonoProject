import logging
import sys

from loguru import logger

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
    def emit(self, record):
        try:
            # Retrieve the corresponding Loguru level if it exists
            level = logger.level(record.levelname).name
        except ValueError:
            # Map standard logging levels to Loguru levels
            level = {
                logging.CRITICAL: "CRITICAL",
                logging.ERROR: "ERROR",
                logging.WARNING: "WARNING",
                logging.INFO: "INFO",
                logging.DEBUG: "DEBUG",
                logging.NOTSET: "NOTSET",
            }.get(record.levelno, logging.INFO)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
