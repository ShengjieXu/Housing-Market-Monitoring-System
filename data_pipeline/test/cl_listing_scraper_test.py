import os
import sys
import logging
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))

import cl_listing_scraper


logger = logging.getLogger(__name__)


class ClListingScraperTestCase(unittest.TestCase):
    def test_get_listings(self):
        scraper = cl_listing_scraper.ListingScraper('sfbay', 'apa')
        count = 0
        for url in scraper.get_listings():
            count += 1
        logger.debug("count=%s", count)
        self.assertGreater(count, 2000)


if __name__ == "__main__":
    logging.basicConfig(filename='cl_listing_scraper_test.log', level=logging.DEBUG)
    unittest.main()
