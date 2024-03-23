import logging
import os

from dotenv import dotenv_values


def get_logger():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    return logging.getLogger(__file__)


def get_config():
    return {
        **dotenv_values(".env"),
        **os.environ
    }
