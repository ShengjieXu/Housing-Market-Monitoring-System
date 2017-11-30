# -*- coding: utf-8 -*-

"""Servie Operations"""

import json
import os
import pickle
import random
import sys

import redis
from bson.json_util import dumps

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "client"))
import mongodb

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "common", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

REDIS_HOST = CONFIG["redis"]["host"]
REDIS_PORT = CONFIG["redis"]["port"]

LISTING_LIMIT = CONFIG["stats"]["average_price"]["listing_limit"]
AVERAGE_PRICES_TIME_OUT_IN_SECONDS = CONFIG["stats"]["average_price"]["time_out_in_seconds"]
MIN_PRICE_THRESHOLD = CONFIG["stats"]["average_price"]["min_price_threshold"]
MAX_PRICE_THRESHOLD = CONFIG["stats"]["average_price"]["max_price_threshold"]

LISTING_TABLE_NAMES = [key for key in CONFIG["craigslist"]["seeds"]]

REDIS_CLIENT = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=0)


def __parse_price(price_str):
    """parse price str --> int"""

    try:
        for i in range(len(price_str)):
            if price_str[i].isdigit():
                number = price_str[i:]
                return int(number) if number.isdigit() else int(float(number))
    except ValueError:
        return -1


def getAverageListingPrices():
    """get the average listing prices for all regions"""

    db = mongodb.get_db()
    average_listing_prices = []

    for region in LISTING_TABLE_NAMES:
        key = region + ":average"

        if REDIS_CLIENT.get(key) is not None:
            current_average = pickle.loads(REDIS_CLIENT.get(key))
        else:
            current_average = {"of": region, "type": "average"}
            listings = list(db[region].find().sort(
                [("available_date", -1)]).limit(LISTING_LIMIT))

            prices = map(lambda x: __parse_price(x["price"]), listings)
            prices = filter(lambda x: MIN_PRICE_THRESHOLD <= x <= MAX_PRICE_THRESHOLD,
                            prices)
            average = 0
            if prices and len(prices) > 0:
                average = sum(prices) / float(len(prices))

            current_average["amount"] = average

            REDIS_CLIENT.set(key, pickle.dumps(current_average))
            REDIS_CLIENT.expire(key, AVERAGE_PRICES_TIME_OUT_IN_SECONDS)

        average_listing_prices.append(current_average)

    return json.loads(dumps(average_listing_prices))
