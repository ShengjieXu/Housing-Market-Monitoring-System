import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))
from region import RegionScraper

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "common", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

class RegionScraperTestCase(unittest.TestCase):
    def test_get_all_regions(self):
        scraper = RegionScraper(CONFIG.get("craigslist").get("about").get("regions_url"))
        regions = scraper.get_all_regions()
        count = len(regions)
        print regions
        print "count=%d" % count
        self.assertGreater(count, 100)


if __name__ == "__main__":
    unittest.main()
