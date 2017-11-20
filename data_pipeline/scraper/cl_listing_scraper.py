# -*- coding: utf-8 -*-

"""A class for monitoring the search page of housing listings"""

import os
import logging
import random
try:
    from urlparse import urljoin  # PY2
except ImportError:
    from urllib.parse import urljoin  # PY3

from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests

import cl_region_scraper

ALL_REGIONS = cl_region_scraper.get_all_regions()
RESULTS_PER_REQUEST = 120

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
        logger.debug("request_detail:params=%s,header=%s", kwargs["params"], headers)
    try:
        return session_requests.get(*args, headers=headers, **kwargs)
    except RequestException as exc:
        if logger:
            logger.warning("Request failed (%s). Retrying ...", exc)
        return session_requests.get(*args, headers=headers, **kwargs)


class ListingScraper(object):
    """A class for monitoring the search page of housing listings"""

    url_templates = "https://%(region)s.craigslist.org/search/%(category)s"

    default_category = "apa"

    def __init__(self, region=None, category=None):
        self.logger = logging.getLogger(__name__)

        self.region = region
        if self.region is None or self.region not in ALL_REGIONS:
            msg = "'%s' is not a valid region" % self.region
            self.logger.error(msg)
            raise ValueError(msg)

        self.category = category or self.default_category

        self.url = self.url_templates % {"region": self.region,
                                         "category": self.category}

    def get_listings(self, limit=None, start=0):
        """scrape listings from the search page"""

        total_so_far = start
        results_yielded = 0
        total = 0

        while True:
            params = {"s": start}
            response = requests_get(self.url, params=params, logger=self.logger)
            self.logger.info("GET %s", response.url)
            self.logger.info("Response code: %s", response.status_code)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            if not total:
                totalcount = soup.find("span", {"class": "totalcount"})
                total = int(totalcount.text) if totalcount else 0

            for listing in soup.find_all("p", {"class": "result-info"}):
                if limit is not None and results_yielded >= limit:
                    break
                self.logger.debug("Processing %s of %s results ...",
                                  total_so_far + 1, total)

                link = listing.find("a", {"class": "hdrlnk"})
                url = urljoin(self.url, link.attrs["href"])
                self.logger.debug("URL=%s", url)

                yield url
                results_yielded += 1
                total_so_far += 1

            if limit is not None and results_yielded >= limit:
                break
            if (total_so_far - start) < RESULTS_PER_REQUEST:
                break
            start = total_so_far
