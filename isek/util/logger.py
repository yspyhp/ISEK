from loguru import logger
import sys
from threading import Lock


class LoggerManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, level="INFO", log_format="{message}"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            cls._instance.__init_logger(level, log_format)
        return cls._instance

    def __init_logger(self, level, log_format):
        logger.remove()
        if log_format:
            logger.add(
                sys.stdout,
                level=level,
                colorize=True,
                format=log_format,
                enqueue=True
            )
        else:
            logger.add(
                sys.stdout,
                level=level,
                colorize=True,
                enqueue=True
            )

    @classmethod
    def init(cls, debug=False):
        level = "DEBUG" if debug else "INFO"
        log_format = None if debug else "{message}"
        cls(level=level, log_format=log_format)

    @staticmethod
    def get_logger():
        return logger


LoggerManager.init(debug=False)

logger = LoggerManager.get_logger()
