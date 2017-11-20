import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))

import cl_region_scraper


class ClRegionScraperTestCase(unittest.TestCase):
    def test(self):
        regions = cl_region_scraper.get_all_regions()
        count = len(regions)
        print regions
        print "count=%d" % count
        self.assertGreater(count, 100)

if __name__ == "__main__":
    unittest.main()
