# -*- coding: utf-8 -*-

"""A generic Scraper that other classes should inherit from"""

import logging
import os
import random

from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

# load and randomize user agents
USER_AGENTS_FILE = os.path.join(os.path.dirname(__file__), "user_agents.txt")
USER_AGENTS = []
with open(USER_AGENTS_FILE, "rb") as uaf:
    for ua in uaf.readlines():
        if ua:
            USER_AGENTS.append(ua.strip()[1:-1])
random.shuffle(USER_AGENTS)


def __get_headers():
    """get request headers"""
    user_agent = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": user_agent
    }
    return headers


def _requests_get(*args, **kwargs):
    """
    Make a session request with a random header
    Retries if a RequestException is raised (could be a connection error or
    a timeout).
    """

    logger = kwargs.pop("logger", None)

    # provide a random header if nothing is given
    headers = kwargs.pop("headers", None)
    if headers is None:
        headers = __get_headers()

    session_requests = requests.session()
    try:
        return session_requests.get(*args, headers=headers, **kwargs)
    except RequestException as exc:
        if logger:
            logger.warning("Request failed (%s). Retrying ...", exc)
        return session_requests.get(*args, headers=headers, **kwargs)


class BaseScraper(object):
    """Base class for all Scrapers"""

    def _get_soup(self, url=None, params=None, headers=None, logger=None):
        """request the page and parse it using BeautifulSoup"""

        response = _requests_get(url, params=params, headers=headers, logger=logger)

        logger = logging.getLogger(__name__)
        logger.info("GET %s", response.url)
        logger.info("Response code: %s", response.status_code)
        response.raise_for_status()

        return BeautifulSoup(response.content, "html.parser")
