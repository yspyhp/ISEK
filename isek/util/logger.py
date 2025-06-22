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
    _initialized = False

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, level="INFO", log_format: str = "{message}"):
        # Only initialize once
        if not self._initialized:
            self._setup_log_levels()
            self._initialized = True
        self._init_logger(level, log_format)

    def _setup_log_levels(self):
        """Setup custom log levels"""
        loguru_logger.level(PRINT_LOG_LEVEL, no=25, color="<cyan>", icon="🖨️")
        loguru_logger.level(NONE_LOG_LEVEL, no=100, color="<white>", icon=" ")

    def _init_logger(self, level, log_format):
        """Initialize the logger with given level and format"""
        loguru_logger.remove()
        if level == NONE_LOG_LEVEL:
            return

        sink_args = {
            "sink": sys.stdout,
            "level": level,
            "colorize": True,
            "enqueue": True,
        }

        # Use provided format or default based on level
        if level == PRINT_LOG_LEVEL:
            sink_args["format"] = log_format or "{message}"
        else:
            sink_args["format"] = (
                log_format
                or "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
            )

        loguru_logger.add(**sink_args)

    @classmethod
    def init(cls, level=PRINT_LOG_LEVEL):
        log_format = (
            "{message}"
            if level == PRINT_LOG_LEVEL
            else "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        return cls(level=level, log_format=log_format)

    @staticmethod
    def get_logger():
        return IsekLogger(loguru_logger)


# Initialize default logger
LoggerManager.init(level=PRINT_LOG_LEVEL)
logger = LoggerManager.get_logger()
