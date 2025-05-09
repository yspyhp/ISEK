from isek.util.logger import LoggerManager, logger

def build(debug=False):
    LoggerManager.init(debug=debug)

    logger.info("Logger initialized with debug mode: {}".format(debug))
    logger.debug("This is a debug message")
    logger.info("This is an info message")


if __name__ == "__main__":
    build(debug=True)