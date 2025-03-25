from isek.util.logger import LoggerManager, logger

def build(debug=False):
    # 根据 `debug` 重新初始化 Logger
    LoggerManager.init(debug=debug)

    logger.info("Logger initialized with debug mode: {}".format(debug))
    logger.debug("This is a debug message")  # 仅在 debug=True 时显示
    logger.info("This is an info message")


if __name__ == "__main__":
    build(debug=True)