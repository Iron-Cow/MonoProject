import logging
import structlog
import sys
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import (
    merge_threadlocal,
)


def configure_logging():
    """Configures the logger to output logs in json and enriches it with additional info"""

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            merge_threadlocal,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            TimeStamper(fmt="iso", utc=True, key="ts"),
            JSONRenderer(sort_keys=True),
        ],

        logger_factory=LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

class Logger:
    """Small helper class to enforce Flinks logging format and encapsulate the logging library"""

    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)

    @staticmethod
    def _create_logging_dict(key: str, story: str, values: dict = {}):
        # add key and story
        new_values = values | {"key": key, "story": story}
        return new_values

    def info(self, key: str, story: str, values: dict = {}):
        self.logger.info(self._create_logging_dict(key, story, values))

    def warn(self, key: str, story: str, values: dict = {}):
        self.logger.warn(self._create_logging_dict(key, story, values))

    def error(self, key: str, story: str, values: dict = {}):
        self.logger.error(self._create_logging_dict(key, story, values))
