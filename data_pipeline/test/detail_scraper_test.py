import os
import sys
import logging
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))
from detail import DetailScraper


class DetailScraperTestCase(unittest.TestCase):
    def test_get_details(self):
        logger = logging.getLogger(__name__)
        scraper = DetailScraper("https://orangecounty.craigslist.org/apa/d/spacious-studio-fully/6396070267.html", "orangecounty", "apa")
        detail = scraper.get_details()
        self.assertEqual(detail["size"], "432ft2")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
