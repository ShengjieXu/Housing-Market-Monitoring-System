# -*- coding: utf-8 -*-

"""Share utility fucntions among scrapers"""

import os
import random

import requests
from requests.exceptions import RequestException

import cl_region_scraper

ALL_REGIONS = cl_region_scraper.get_all_regions()

USER_AGENTS_FILE = os.path.join(os.path.dirname(__file__), "user_agents.txt")
USER_AGENTS = []

with open(USER_AGENTS_FILE, "rb") as uaf:
    for ua in uaf.readlines():
        if ua:
            USER_AGENTS.append(ua.strip()[1:-1])
random.shuffle(USER_AGENTS)


def get_headers():
    """get request headers"""
    user_agent = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": user_agent
    }
    return headers


def requests_get(*args, **kwargs):
    """
    Retries if a RequestException is raised (could be a connection error or
    a timeout).
    """

    logger = kwargs.pop("logger", None)
    session_requests = requests.session()
    headers = get_headers()
    if logger:
        logger.debug("request_detail:params=%s,header=%s", kwargs.get("params"), headers)
    try:
        return session_requests.get(*args, headers=headers, **kwargs)
    except RequestException as exc:
        if logger:
            logger.warning("Request failed (%s). Retrying ...", exc)
        return session_requests.get(*args, headers=headers, **kwargs)
