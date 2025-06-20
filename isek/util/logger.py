from loguru import logger as loguru_logger
import sys
from threading import Lock


PRINT_LOG_LEVEL = "PRINT"
NONE_LOG_LEVEL = "NONE"


class IsekLogger:
    def __init__(self, base_logger):
        self._logger = base_logger

    def print(self, message, *args, **kwargs):
        return self._logger.log(PRINT_LOG_LEVEL, message, *args, **kwargs)

    def debug(self, *args, **kwargs):
        return self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._logger.error(*args, **kwargs)

    def exception(self, *args, **kwargs):
        return self._logger.exception(*args, **kwargs)

    def log(self, *args, **kwargs):
        return self._logger.log(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._logger, name)


class LoggerManager:
    _instance = None
    _lock = Lock()
    loguru_logger.level(PRINT_LOG_LEVEL, no=25, color="<cyan>", icon="🖨️")
    loguru_logger.level(NONE_LOG_LEVEL, no=100, color="<white>", icon=" ")

    def __new__(cls, level="INFO", log_format="{message}"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            cls._instance.__init_logger(level, log_format)
        return cls._instance

    def __init_logger(self, level, log_format):
        loguru_logger.remove()
        if level == NONE_LOG_LEVEL:
            return
        sink_args = {
            "sink": sys.stdout,
            "level": level,
            "colorize": True,
            "enqueue": True,
        }

        if level == PRINT_LOG_LEVEL:
            sink_args["format"] = "{message}"
            # sink_args["filter"] = lambda record: record["level"].name == PRINT_LOG_LEVEL

        loguru_logger.add(**sink_args)

    @classmethod
    def init(cls, level=PRINT_LOG_LEVEL):
        log_format = None if level != PRINT_LOG_LEVEL else "{message}"
        cls(level=level, log_format=log_format)

    @staticmethod
    def get_logger():
        return IsekLogger(loguru_logger)


LoggerManager.init(level=PRINT_LOG_LEVEL)
logger = LoggerManager.get_logger()
