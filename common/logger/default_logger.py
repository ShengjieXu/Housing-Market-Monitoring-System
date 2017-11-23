# -*- coding: utf-8 -*-

"""Config default loggers"""

import logging


def set_default_dual_logger(filename="default.log", filemode="a"):
    """
    Default: log DEBUG and higher message to the file, "a" mode,
             log INFO and higher message to the console
    """

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                        datefmt="%m-%d %H:%M",
                        filename=filename,
                        filemode=filemode)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    fmter = logging.Formatter(fmt="%(name)-12s %(levelname)-8s %(message)s")
    console_handler.setFormatter(fmter)

    logging.getLogger("").addHandler(console_handler)


def set_default_console_logger():
    """
    Default: log INFO and higher message to the console
    """

    logging.basicConfig(level=logging.INFO,
                        format="%(name)-12s %(levelname)-8s %(message)s")

