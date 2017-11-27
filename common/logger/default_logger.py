# -*- coding: utf-8 -*-

"""Config default loggers"""

import logging
import logging.handlers


def set_default_dual_logger(filename="default.log"):
    """
    Default: log DEBUG and higher message to the file, "a" mode,
             log INFO and higher message to the console
    """

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.RotatingFileHandler(filename,
                                                        maxBytes=100000000,
                                                        backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_fmter = logging.Formatter(fmt="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                                   datefmt="%m-%d %H:%M")
    file_handler.setFormatter(file_fmter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmter = logging.Formatter(fmt="%(name)-12s %(levelname)-8s %(message)s")
    console_handler.setFormatter(console_fmter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def set_default_console_logger():
    """
    Default: log INFO and higher message to the console
    """

    logging.basicConfig(level=logging.INFO,
                        format="%(name)-12s %(levelname)-8s %(message)s")
