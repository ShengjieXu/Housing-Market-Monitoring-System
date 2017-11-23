# -*- coding: utf-8 -*-

"""A class for monitoring the search page of housing listings"""

import logging
try:
    from urlparse import urljoin  # PY2
except ImportError:
    from urllib.parse import urljoin  # PY3

from bs4 import BeautifulSoup

import cl_common


class ListingScraper(object):
    """A class for monitoring the search page of housing listings"""

    url_templates = "https://%(region)s.craigslist.org/search/%(category)s"

    default_category = "apa"

    def __init__(self, region=None, category=None):
        self.logger = logging.getLogger(__name__)

        self.region = region
        if self.region is None or self.region not in cl_common.ALL_REGIONS:
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

        params = {"s": start}
        response = cl_common.requests_get(self.url, params=params, logger=self.logger)
        self.logger.info("GET %s", response.url)
        self.logger.info("Response code: %s", response.status_code)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        if not total:
            totalcount = soup.find("span", {"class": "totalcount"})
            total = int(totalcount.text) if totalcount else 0

        for row in soup.find_all("p", {"class": "result-info"}):
            if limit is not None and results_yielded >= limit:
                break
            self.logger.debug("Processing %s of %s results ...", total_so_far + 1, total)

            link = row.find("a", {"class": "hdrlnk"})
            url = urljoin(self.url, link.attrs["href"])
            self.logger.debug("URL=%s", url)

            results_yielded += 1
            total_so_far += 1
            listing = {"url": url, "total_so_far": total_so_far}
            yield listing
