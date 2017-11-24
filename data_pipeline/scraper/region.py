# -*- coding: utf-8 -*-

"""A class for Scraping all regions of Craigslist"""

import logging

from base import BaseScraper


class RegionScraper(BaseScraper):
    """A class for Scraping all regions of Craigslist"""

    def __init__(self, regions_url):
        self.regions_url = regions_url

    def get_all_regions(self):
        """scrape all regions"""

        regions = set()
        soup = self._get_soup(url=self.regions_url, logger=logging.getLogger(__name__))

        for box in soup.findAll("div", {"class": "box"}):
            for a in box.findAll("a"):
                # Remove protocol and get subdomain
                region = a.attrs["href"].rsplit("//", 1)[1].split(".")[0]
                regions.add(region)

        return regions
