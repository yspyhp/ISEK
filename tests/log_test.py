from isek.util.logger import LoggerManager, logger


def test_build(debug=False):
    LoggerManager.init(debug=debug)

    logger.info("Logger initialized with debug mode: {}".format(debug))
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    return True
