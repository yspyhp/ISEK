from loguru import logger as loguru_logger  # Rename to avoid conflict
import sys
from threading import Lock
from typing import Optional, ClassVar, Any  # Added Any


class LoggerManager:
    """
    A singleton manager for configuring the global Loguru logger.

    This class ensures that logger configuration is applied consistently.
    Use the `LoggerManager.init()` class method to configure the logger.
    Access the configured logger via `LoggerManager.get_logger()` or the
    globally exported `logger` instance from this module.
    """

    _instance: ClassVar[Optional["LoggerManager"]] = None
    _lock: ClassVar[Lock] = Lock()
    _configured_level: ClassVar[str] = "INFO"  # Store current config state
    _configured_format: ClassVar[Optional[str]] = "{message}"

    # __new__ only creates the instance if it doesn't exist.
    # Configuration is now handled by a separate method called from init.
    def __new__(cls, *args: Any, **kwargs: Any) -> "LoggerManager":
        """
        Ensures only one instance of LoggerManager is created (Singleton).
        Actual logger configuration should be done via the `init` class method.
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # print("LoggerManager singleton instance created.") # Debug
        return cls._instance

    # __init__ is generally not needed for this type of singleton if
    # state is managed at the class level or configuration is via a dedicated method.
    # def __init__(self):
    #     pass # No instance-specific initialization needed here

    @classmethod
    def _configure_logger(cls, level: str, log_format: Optional[str]) -> None:
        """
        Internal class method to actually configure the Loguru logger.
        This is called by `init`.

        :param level: The logging level string (e.g., "INFO", "DEBUG").
        :type level: str
        :param log_format: The Loguru format string. If None, Loguru's default rich format is used.
        :type log_format: typing.Optional[str]
        """
        with cls._lock:  # Protect access to global Loguru configuration
            try:
                loguru_logger.remove()  # Remove all existing handlers
            except ValueError:  # Raised if no handlers to remove (Loguru <0.6.0)
                pass

            sink_args = {
                "sink": sys.stdout,
                "level": level.upper(),
                "colorize": True,
                "enqueue": True,
            }

            if log_format:
                sink_args["format"] = log_format

            # For non-debug (INFO level), we want INFO and higher.
            # For DEBUG level, we want DEBUG and higher (which Loguru does by default).
            # The filter is only needed if you want to *strictly* log only one level,
            # which is not the case for standard INFO or DEBUG settings.
            # If level is INFO, messages of level INFO, WARNING, ERROR, CRITICAL will pass.
            # If level is DEBUG, messages of level DEBUG, INFO, ... will pass.

            loguru_logger.add(**sink_args)
            cls._configured_level = level.upper()
            cls._configured_format = log_format
            # print(f"Loguru logger configured. Level: {cls._configured_level}, Format: '{cls._configured_format if cls._configured_format else 'Loguru Default'}'") # Debug

    @classmethod
    def init(cls, debug: bool = False) -> None:
        """
        Initializes or reconfigures the global Loguru logger.

        Sets the logging level to "DEBUG" if `debug` is True, otherwise "INFO".
        Uses Loguru's default rich format if `debug` is True, otherwise uses
        a minimal "{message}" format.

        :param debug: If `True`, sets log level to "DEBUG" and uses Loguru's default rich format.
                      If `False`, sets log level to "INFO" and uses "{message}" format.
                      Defaults to `False`.
        :type debug: bool
        """
        level = "DEBUG" if debug else "INFO"
        # If debug, use Loguru's default rich format (by passing None for format).
        # Otherwise, use minimal "{message}".
        log_format = None if debug else "{message}"

        # Ensure instance exists, then configure.
        cls()  # This calls __new__ to ensure _instance is created.
        cls._configure_logger(level=level, log_format=log_format)

    @staticmethod
    def get_logger():  # No type hint needed for Loguru's dynamic logger object
        """
        Provides access to the globally configured Loguru logger instance.

        :return: The Loguru logger instance.
        """
        return loguru_logger


# --- Global Logger Instance ---
# Initialize logger on module import with default non-debug settings.
LoggerManager.init(debug=False)

# Provide a globally accessible logger instance from this module.
# Users can `from isek.util.logger import logger`
logger = LoggerManager.get_logger()

# Example Usage (can be removed from the final module)
if __name__ == "__main__":
    print("--- Initial (default) logger config ---")
    logger.debug("This is a debug message (should not appear).")
    logger.info("This is an info message (default format).")
    logger.warning("This is a warning message.")

    print("\n--- Reconfiguring to DEBUG mode ---")
    LoggerManager.init(debug=True)
    logger.debug("This is a debug message (should appear now, rich format).")
    logger.info("This is an info message (rich format).")

    print("\n--- Reconfiguring back to non-DEBUG mode ---")
    LoggerManager.init(debug=False)
    logger.debug("This is a debug message (should not appear again).")
    logger.info("This is an info message (minimal format again).")
    logger.error("This is an error message.")
