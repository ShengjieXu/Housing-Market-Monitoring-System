# -*- coding: utf-8 -*-

"""Deduplicate listings and filter out listings without useful information"""

import json
import logging
import os
import pprint
import sys

from dateutil import parser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "client"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "logger"))
from cloudamqp import CloudAMQPClient
from default_logger import set_default_dual_logger
import mongodb

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "common", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

DEDUPE_LISTINGS_TASK_QUEUE_URL = CONFIG["cloudamqp"]["dedupe_listings_task_queue"]["url"]
DEDUPE_LISTINGS_TASK_QUEUE_NAME = CONFIG["cloudamqp"]["dedupe_listings_task_queue"]["name"]

CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS = CONFIG["listing"]["deduper"]["interval_in_seconds"]

MONGODB_URI = CONFIG["mongodb"]["uri"]

LISTING_TTL_IN_DAYS = CONFIG["listing"]["time_to_live"]["days"]

LOG_FILE_NAME = "listing_deduper.log"


def _handle_task(task):
    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    1. Dedupe logic:
        Discard listings without price or craigslist_id or img_url or title or available_date
        if same (craigslist_id) or (url) or (img_url, not empty) or (title, not empty) exist:
            if new_available_date - old_available_date >= LISTING_TTL:
                insert as new
            else:
                skipping...
        else:
            insert as new
    2. Skip geocoding at least for now, because 792 out of 8,910 results (9%) don't have geo,
    ALL of them don't have street addresses, which makes geocoding meaningless as the
    information would be very ambiguous. Besides, Craigslist has already geocoded listings in
    the creation time. We can just use what is provided.
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Analysis based on 8,910 samples from sfbay, newyork, losangeles on Sat Nov 25, 2017:
    Duplicates indicators:
        same craigslist_id: 3 (<0.1%) => must be duplicates
            Very similiar url with the same Craigslist id, probably posted by bots
        same url: 0, good job redis! ;)
        same img_url: 8910 - 5,538(unique) - 554(no img) = 2818 (32%) => must be duplicates
            Craigslist uses the same img url if the same image is used in different posts.
            Listings without img account for 6%
                include them => possibile introduce duplicates, affect stats
                discard them => only lose small amout of info, but less duplicates
            e.g. this person posted the same house for 19 times.
            https://losangeles.craigslist.org/lac/apa/d/beautifull-5-bed-2-bath/6392306996.html
            https://losangeles.craigslist.org/lac/apa/d/beautifull-5-bed-2-bath/6386058564.html
            https://losangeles.craigslist.org/lac/apa/d/beautifull-5-bed-2-bath/6386058372.html
            https://losangeles.craigslist.org/lac/apa/d/beautifull-5-bed-2-bath/6382192769.html
            https://losangeles.craigslist.org/lac/apa/d/beautifull-5-bed-2-bath-for/6386988925.html
            ...
        same title: 8910 - 7266(unique) = 1,644 (18%) => must be duplicates
            Title cannot be null per Craigslist's requirements
            e.g. the following listings point to a same house and all have the same title
            https://newyork.craigslist.org/fct/abo/d/studio-apt-private-entrance/6390365538.html
            https://newyork.craigslist.org/fct/abo/d/studio-apt-private-entrance/6388979401.html
            https://newyork.craigslist.org/fct/abo/d/studio-apt-private-entrance/6387791128.html
            https://newyork.craigslist.org/fct/abo/d/studio-apt-private-entrance/6387795959.html
        listings WIHTOUT available date: 83 (0.9%)

        Some other stats for fun:
            same geo: 8910 - 3438(unique) - 792(empty) = 4680 (53%)
                But geo can be very inaccurate...
            same price: 8910 - 767(unique) - 91(empty) = 8052 (90%)
            same size: 8910 - 396(unique) - 3653(empty) = 4861 (55%)
            same street: 8910 - 2574(unique) - 2612(empty) = 3724 (42%)
    """

    logger = logging.getLogger(__name__)
    listing = json.loads(task)

    if listing["craigslist_id"] and listing["price"] and listing["img_url"] and listing["title"] and listing["available_date"]:
        db = mongodb.get_db()
        table_name = listing["region"]
        existings = list(db[table_name].find({"$or": [{"craigslist_id": listing["craigslist_id"]},
                                                      {"url": listing["url"]},
                                                      {"img_url": listing["img_url"]},
                                                      {"title": listing["title"]}]
                                             }))
        for existing in existings:
            new_available_date = parser.parse(listing["available_date"])
            old_available_date = parser.parse(existing["available_date"])
            if (new_available_date - old_available_date).days <= LISTING_TTL_IN_DAYS:
                logger.debug("Skipping duplicate... %s<=TTL: existing=%s, incoming=%s",
                             (new_available_date - old_available_date).days,
                             existing, listing)
                return
        db[table_name].insert_one(listing)
        logger.debug("Inserting, table_name=%s, listing=%s", table_name, listing)
    else:
        logger.info("Skipping no useful info, listing=%s", listing)


def dedupe():
    """get task from dedupe_listings_task_queue and handle task"""

    logger = logging.getLogger(__name__)
    cloudamqp_client = CloudAMQPClient(DEDUPE_LISTINGS_TASK_QUEUE_URL,
                                       DEDUPE_LISTINGS_TASK_QUEUE_NAME,
                                       durable=True)

    while True:
        if cloudamqp_client:
            task = cloudamqp_client.get(as_str=True)
            if task:
                try:
                    _handle_task(task)
                except (SystemExit, KeyboardInterrupt):
                    cloudamqp_client.close()
                    raise
                except Exception:
                    logger.error("Failed to handle task=%s, skipping...",
                                 pprint.pformat(task), exc_info=True)
            else:
                logger.debug("No dedupe task returned. Sleeping...")
            cloudamqp_client.sleep(CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS)
        else:
            logger.info("Connection to the CloudAMQP client is lost. Terminating...")
            break


if __name__ == "__main__":
    set_default_dual_logger(LOG_FILE_NAME)
    logging.getLogger("pika").setLevel(logging.WARNING)
    dedupe()
