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
        logger.remove()  # 移除默认的日志处理
        if log_format:
            logger.add(
                sys.stdout,
                level=level,
                colorize=True,
                format=log_format,
                enqueue=True  # 线程安全
            )
        else:
            logger.add(
                sys.stdout,
                level=level,
                colorize=True,
                enqueue=True  # 线程安全
            )

    @classmethod
    def init(cls, debug=False):
        """初始化 logger, 支持动态配置"""
        level = "DEBUG" if debug else "INFO"
        log_format = None if debug else "{message}"
        cls(level=level, log_format=log_format)  # 创建单例

    @staticmethod
    def get_logger():
        return logger


# 默认初始化为 INFO，防止未初始化时无法使用
LoggerManager.init(debug=False)

# 直接导出 logger，供其他模块使用
logger = LoggerManager.get_logger()
