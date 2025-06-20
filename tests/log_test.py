from isek.util.logger import LoggerManager, logger


def build():
    # LoggerManager.init(debug=debug)
    level = "NONE"
    LoggerManager.init(level=level)
    logger.info("Logger initialized with debug mode: {}".format(level))
    logger.print("This is a print message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")


build()
