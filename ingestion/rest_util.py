#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import logger_util

logger = logger_util.get_logger("rest_util")

MAX_RETRY_ATTEMPT = 5
RATE_LIMIT = 1


def get_pdf(url):
    """
    Sends a GET request to a URL.

    :param url: URL

    :type url: str

    :returns: PDF URLs
    :rtype: dict | list

    :return:
    """
    i = 0
    while i < MAX_RETRY_ATTEMPT:
        try:

            return requests.request("GET", url)

        except requests.exceptions.HTTPError as e:
            logger.error("Error in get_pdf() " + str(e))
        except requests.exceptions.ConnectionError as e:
            logger.error("Error in get_pdf() " + str(e))
            time.sleep(RATE_LIMIT)

        i = i + 1
        logger.info("retrying attempt {}..".format(str(i)))
    else:
        logger.error("get_pdf() - Max retry limit breached.")
