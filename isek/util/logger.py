from loguru import logger as loguru_logger # Rename to avoid conflict with global logger
import sys
from threading import Lock
from typing import Optional, ClassVar # Added ClassVar


class LoggerManager:
    """
    A singleton manager for configuring the Loguru logger.

    This class ensures that there is only one instance of the logger configuration
    manager. It provides methods to initialize and re-initialize the global
    Loguru logger with specified levels, formats, and sinks.

    The `init` class method is the primary way to configure the logger.
    The `get_logger` static method provides access to the configured
    Loguru logger instance.

    Upon import of this module, the logger is initialized with a default
    configuration (INFO level, "{message}" format).
    """
    _instance: ClassVar[Optional['LoggerManager']] = None
    _lock: ClassVar[Lock] = Lock()

    # This __new__ method is a bit unusual for how Loguru is typically configured.
    # Loguru's logger is global. Re-calling __new__ or __init__ on this manager
    # will reconfigure the *same* global Loguru logger.
    # The singleton pattern here manages the *configuration state* if needed,
    # but the logger itself is already a global entity managed by Loguru.
    def __new__(cls, level: str = "INFO", log_format: Optional[str] = "{message}") -> 'LoggerManager':
        """
        Creates or returns the singleton instance of LoggerManager.

        Each time this is called (even with different parameters), it will
        re-initialize the global Loguru logger using the provided `level`
        and `log_format`.

        :param level: The logging level (e.g., "DEBUG", "INFO", "WARNING").
                      Defaults to "INFO".
        :type level: str
        :param log_format: The Loguru format string for log messages.
                           If `None`, a default Loguru format might be used (though
                           the implementation currently adds a default sink even if format is None).
                           Defaults to "{message}".
        :type log_format: typing.Optional[str]
        :return: The singleton LoggerManager instance.
        :rtype: LoggerManager
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # Initial configuration happens here on first instance creation.
                # Subsequent calls to __new__ will get the existing instance
                # but __init_logger will still be called by the __new__ method's logic.
            
            # This effectively makes __new__ also re-initialize the logger.
            # If the intent is for __init__ to only run once, this should be different.
            # However, the current pattern means calling LoggerManager() reconfigures.
            cls._instance.__init_logger_internal(level, log_format) # Renamed to avoid confusion with __init__
        return cls._instance

    # __init__ is typically called after __new__. If you want __init__ to do something
    # only once per instance, you'd add a flag.
    # Given the __new__ reconfigures, this __init__ might not be strictly necessary
    # if all config is passed to __new__.
    # For clarity, let's assume __init__ isn't doing much if __new__ handles config.
    # def __init__(self, level: str = "INFO", log_format: Optional[str] = "{message}"):
    #     """
    #     Initializes the LoggerManager instance.
    #
    #     Note: The actual logger configuration is primarily handled in `__new__`
    #     via `__init_logger_internal` in this specific singleton implementation.
    #     This `__init__` method would be called every time `LoggerManager()` is invoked
    #     after `__new__` returns the instance.
    #
    #     :param level: The logging level.
    #     :type level: str
    #     :param log_format: The Loguru format string.
    #     :type log_format: typing.Optional[str]
    #     """
    #     # If self.configured flag is used:
    #     # if not hasattr(self, '_configured'):
    #     #     self.__init_logger_internal(level, log_format)
    #     #     self._configured = True
    #     pass


    def __init_logger_internal(self, level: str, log_format: Optional[str]) -> None:
        """
        Internal method to initialize or re-initialize the Loguru logger.

        Removes any existing handlers and adds a new one to `sys.stdout`
        with the specified level and format.

        :param level: The logging level string (e.g., "INFO", "DEBUG").
        :type level: str
        :param log_format: The Loguru format string for log messages.
                           If `None`, a basic Loguru format is used (which might
                           include more than just the message by default if not specified).
        :type log_format: typing.Optional[str]
        """
        # Use the renamed loguru_logger to avoid conflict
        loguru_logger.remove() # Removes all previously added handlers
        
        # Common sink arguments
        sink_args = {
            "sink": sys.stdout,
            "level": level.upper(), # Ensure level is uppercase for Loguru
            "colorize": True,
            "enqueue": True # Useful for thread-safety and performance in some cases
        }

        if log_format:
            sink_args["format"] = log_format
        # If log_format is None, Loguru uses its default rich format.
        # The original code had an `else` block that added the logger without the format string,
        # which is equivalent to letting Loguru use its default when `format` is not in sink_args.

        loguru_logger.add(**sink_args)
        # print(f"Loguru logger re-initialized. Level: {level.upper()}, Format: '{log_format if log_format else 'Loguru Default'}'") # Debug

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
        
        # Calling cls() invokes __new__ which in turn calls __init_logger_internal
        cls(level=level, log_format=log_format)

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