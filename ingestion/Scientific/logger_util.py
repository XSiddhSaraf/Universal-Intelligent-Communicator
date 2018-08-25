#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import sys

DEFAULT_FORMAT = "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
DEFAULT_STREAM = sys.stdout
DEFAULT_LEVEL = logging.INFO


def get_logger(log_name, format=DEFAULT_FORMAT, stream=DEFAULT_STREAM, level=DEFAULT_LEVEL):
    """
    Gets a logger.

    :param log_name: name of the logger
    :param format: log format
    :param stream: log stream
    :param level: log level

    :type log_name: str
    :type format: str
    :type stream: io.TextIOWrapper
    :type level: int

    :returns: logger
    :rtype: logging.Logger
    """
    logging.basicConfig(format=format, stream=stream)
    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    return logger
