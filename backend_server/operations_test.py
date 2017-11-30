# -*- coding: utf-8 -*-

"""Basic testing for operations"""

import os
import sys
import logging
import unittest

import operations

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "common", "client"))
import mongodb


class OperationsTestCase(unittest.TestCase):
    def test_getAverageListingPrices(self):
        logger = logging.getLogger(__name__)
        avg_prices = operations.getAverageListingPrices()
        logger.info(avg_prices)
        self.assertGreaterEqual(len(avg_prices), 7)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
