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

STATS_LISTINGS_LIMIT = CONFIG["stats"]["average_price"]["listing_limit"]
MARKETS_STATS_TIME_OUT_IN_SECONDS = CONFIG["stats"]["average_price"]["time_out_in_seconds"]
MIN_PRICE_THRESHOLD = CONFIG["stats"]["average_price"]["min_price_threshold"]
MAX_PRICE_THRESHOLD = CONFIG["stats"]["average_price"]["max_price_threshold"]

MARKETS_LISTINGS_LIMIT = CONFIG["markets"]["listings"]["limit"]
MARKETS_LISTINGS_TIME_OUT_IN_SECONDS = CONFIG["markets"]["listings"]["time_out_in_seconds"]

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
    statistics_average = {
        "type": "average",
        "payloads": []
    }

    for region in LISTING_TABLE_NAMES:
        key = "api/v1/markets/stats/average/" + region

        if REDIS_CLIENT.get(key) is not None:
            payload = pickle.loads(REDIS_CLIENT.get(key))
        else:
            payload = {"region": region, "count": 0, "data": 0}

            listings = list(db[region].find().sort(
                [("available_date", -1)]).limit(STATS_LISTINGS_LIMIT))
            prices = filter(lambda x: MIN_PRICE_THRESHOLD <= x <= MAX_PRICE_THRESHOLD,
                            map(lambda x: __parse_price(x["price"]), listings))

            if prices and len(prices) > 0:
                payload["data"] = sum(prices) / float(len(prices))
                payload["count"] = len(prices)

            REDIS_CLIENT.set(key, pickle.dumps(payload))
            REDIS_CLIENT.expire(key, MARKETS_STATS_TIME_OUT_IN_SECONDS)

        statistics_average["payloads"].append(payload)

    return json.loads(dumps(statistics_average))


def getListings(region):
    """get recent listings for the given region"""

    db = mongodb.get_db()
    listings_region = {
        "region": region,
        "payloads": []
    }

    key = "api/v1/markets/listings/" + region
    if REDIS_CLIENT.get(key) is not None:
        payloads = pickle.loads(REDIS_CLIENT.get(key))
    else:
        listings = list(db[region].find().sort(
            [("available_date", -1)]).limit(MARKETS_LISTINGS_LIMIT))
        payloads = map(lambda x: {
            "url": x["url"],
            "title": x["title"],
            "price": x["price"],
            "geo": x["geo"],
            "bed": x["bed"],
            "bath": x["bath"],
            "available_date": x["available_date"],
            "img_url": x["img_url"]
            }, listings)

        REDIS_CLIENT.set(key, pickle.dumps(payloads))
        REDIS_CLIENT.expire(key, MARKETS_LISTINGS_TIME_OUT_IN_SECONDS)

    listings_region["payloads"] = payloads

    return json.loads(dumps(listings_region))
