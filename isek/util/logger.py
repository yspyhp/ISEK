from loguru import logger as loguru_logger # Rename to avoid conflict with global logger
import sys
from threading import Lock
from typing import Optional, ClassVar # Added ClassVar


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
    def init(cls, debug: bool = False) -> None:
        """
        Convenience class method to initialize/reconfigure the global logger.

        Sets the logging level to "DEBUG" if `debug` is True, otherwise "INFO".
        Sets a minimal log format ("{message}") if not in debug mode, otherwise
        allows Loguru's richer default format by passing `None` for `log_format`.

        :param debug: If `True`, sets log level to "DEBUG" and uses Loguru's default rich format.
                      If `False`, sets log level to "INFO" and uses "{message}" format.
                      Defaults to `False`.
        :type debug: bool
        """
        level = "DEBUG" if debug else "INFO"
        # If debug, use Loguru's default rich format. Otherwise, use minimal "{message}".
        log_format = None if debug else "{message}"
        cls(debug=debug)

    @staticmethod
    def get_logger(): # No type hint for return as it's Loguru's dynamic logger object
        """
        Provides access to the globally configured Loguru logger instance.

        :return: The Loguru logger instance.
        """
        return loguru_logger # Return the renamed Loguru logger

# --- Global Logger Instance ---
# Initialize logger on module import with default non-debug settings.
# This ensures 'logger' is available immediately.
LoggerManager.init(debug=False)

# Provide a globally accessible logger instance from this module.
# Users can `from isek.util.logger import logger`
logger = LoggerManager.get_logger()