import os
import sys
import logging
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))
from detail import DetailScraper


class DetailScraperTestCase(unittest.TestCase):
    def setUp(self):
        self.tasks = [{"url": "https://orangecounty.craigslist.org/apa/d/spacious-studio-fully/6396070267.html",
                       "region": "orangecounty",
                       "category": "apa"}, {
                        "url": "https://orangecounty.craigslist.org/apa/d/title/6398911602.html",
                        "region": "orangecounty",
                        "category": "apa"
                       }, {
                        "url": "https://newyork.craigslist.org/brk/abo/d/perfect-3brno/6390308280.html",
                        "region": "newyork",
                        "category": "aap"
                       }, {
                        "url": "https://losangeles.craigslist.org/sfv/apa/d/modern-remodeled-unit-in/6368859107.html",
                        "region": "losangeles",
                        "category": "apa"
                       }]

    def test_get_details(self):
        logger = logging.getLogger(__name__)
        for task in self.tasks:
            scraper = DetailScraper(url=task["url"], region=task["region"], category=task["category"])
            logger.info("Testing region=%s, url=%s", task["region"], task["url"])
            detail = scraper.get_details()
            self.assertEqual(detail["url"], task["url"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
