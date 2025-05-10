from loguru import logger
import sys
from threading import Lock


class LoggerManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, debug=False):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            cls._instance.__init_logger(debug)
        return cls._instance

    def __init_logger(self, debug=False):
        logger.remove()
        if debug:
            logger.add(sys.stdout, level="DEBUG", colorize=True, enqueue=True)
        else:
            logger.add(
                sys.stdout,
                level="INFO",
                colorize=True,
                enqueue=True,
                format="{message}",
                filter=lambda record: record["level"].no == logger.level("INFO").no
            )

    @classmethod
    def init(cls, debug=False):
        level = "DEBUG" if debug else "INFO"
        log_format = None if debug else "{message}"
        cls(debug=debug)

    @staticmethod
    def get_logger():
        return logger


LoggerManager.init(debug=False)

logger = LoggerManager.get_logger()
