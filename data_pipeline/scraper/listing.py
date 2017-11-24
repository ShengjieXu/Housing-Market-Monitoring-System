# -*- coding: utf-8 -*-

"""A class for scraping the search page of housing listings"""

import json
import logging
import os
try:
    from urlparse import urljoin  # PY2
except ImportError:
    from urllib.parse import urljoin  # PY3

from base import BaseScraper
from region import RegionScraper

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "common", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

REGION_SCRAPER = RegionScraper(CONFIG.get("craigslist").get("about").get("regions_url"))
ALL_REGIONS = REGION_SCRAPER.get_all_regions()


class ListingScraper(BaseScraper):
    """A class for scraping the search page of housing listings"""

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
        """Get all listing-urls from the given listing page"""

        total_so_far = start
        results_yielded = 0
        total = 0

        params = {"s": start}
        soup = self._get_soup(url=self.url, params=params, logger=self.logger)

        if total == 0:
            totalcount = soup.find("span", {"class": "totalcount"})
            total = int(totalcount.text) if totalcount else 0

        for row in soup.find_all("p", {"class": "result-info"}):
            if limit is not None and results_yielded >= limit:
                break
            self.logger.debug("Processing %s of %s results ...", total_so_far + 1, total)

            link = row.find("a", {"class": "hdrlnk"})
            url = urljoin(self.url, link.attrs["href"])

            results_yielded += 1
            total_so_far += 1
            listing = {"url": url, "total_so_far": total_so_far,
                       "region": self.region, "category": self.category}

            self.logger.debug("Yielding listing=%s", listing)
            yield listing
