import os
import sys
import logging
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))
from listing import ListingScraper


class ListingScraperTestCase(unittest.TestCase):
    def test_get_listings(self):
        logger = logging.getLogger(__name__)
        scraper = ListingScraper('sfbay', 'apa')
        count = 0
        for url in scraper.get_listings():
            count += 1
        logger.info("count=%s", count)
        self.assertGreater(count, 100)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
