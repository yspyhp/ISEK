import logging
from os import getenv
from threading import Lock
from typing import Any, cast

from rich.console import Console
from rich.logging import RichHandler

# --- Constants ---
LOGGER_NAME = "isek"
TEAM_LOGGER_NAME = f"{LOGGER_NAME}-team"

# --- Rich Console ---
console = Console()


# --- Custom Logger Class ---
class IsekLogger(logging.Logger):
    """
    Custom logger class with a `print` method for rich console output.
    """

    def print(self, message: Any, *args, **kwargs):
        """Prints a message to the rich console."""
        console.print(message, *args, **kwargs)


# --- Centralized Logger Manager ---
class LoggerManager:
    """
    Manages logger configuration and instances.
    Ensures a single, configurable logging setup using rich for output.

    Usage:
        from isek.utils.log import log, team_log

        log.info("This is an agent log message.")
        team_log.info("This is a team log message.")

        log.print("[bold green]This is a rich message![/bold green]")

        LoggerManager.set_level("DEBUG", name="agent")
        log.debug("This is a debug message.")
    """

    _loggers = {}
    _lock = Lock()

    @classmethod
    def get_logger(cls, name: str = "agent") -> IsekLogger:
        """
        Retrieves a logger instance by name ('agent' or 'team').
        Initializes the logger on first use.
        """
        with cls._lock:
            logger_key = name.lower()
            if logger_key not in ["agent", "team"]:
                raise ValueError("Logger name must be 'agent' or 'team'.")

            if logger_key not in cls._loggers:
                cls._loggers[logger_key] = cls._create_logger(logger_key)

            return cast(IsekLogger, cls._loggers[logger_key])

    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Creates and configures a new logger instance."""
        logger_name = LOGGER_NAME if name == "agent" else TEAM_LOGGER_NAME
        logging.setLoggerClass(IsekLogger)
        logger = logging.getLogger(logger_name)
        logging.setLoggerClass(logging.Logger)  # Reset

        log_level_str = getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level_str, logging.INFO))

        rich_handler = RichHandler(
            console=console,
            show_time=False,
            rich_tracebacks=True,
            show_path=False,
            markup=True,
        )
        rich_handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))

        logger.handlers.clear()
        logger.addHandler(rich_handler)
        logger.propagate = False

        return logger

    @classmethod
    def set_level(cls, level: str, name: str = "agent"):
        """Sets the logging level for a specific logger."""
        logger = cls.get_logger(name)
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)


# --- Default logger instances for convenience ---
log = LoggerManager.get_logger("agent")
team_log = LoggerManager.get_logger("team")
# For backward compatibility
logger = log
