# -*- coding: utf-8 -*-

"""housing listing monitor"""

import threading
import logging
import os
import sys
try:
    from Queue import Queue  # PY2
except ImportError:
    from queue import Queue  # PY3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "client"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scraper"))

import redis
from six import iteritems
from six.moves import range

from cloudamqp import CloudAMQPClient
from cl_listing_scraper import ListingScraper

REDIS_HOST = "localhost"
REDIS_PORT = 6379

SLEEP_TIME_IN_SECONDS = 3600 * 6
LISTING_TIME_OUT_IN_SECONDS = 3600 * 24 * 3

SCRAPE_LISTINGS_TASK_QUEUE_URL = "amqp://zsjdmkfu:x1LwP5IRoZjs7C1LWpMK7_87OdxLoQnM@donkey.rmq.cloudamqp.com/zsjdmkfu"
SCRAPE_LISTINGS_TASK_QUEUE_NAME = "hmms-scrape-listings-task-queue"

# Craigslist return 120 results per request
RESULTS_PER_REQUEST = 120

NUM_OF_WORKER_THREADS = 8

"""
craigslist scraping seeds
~~~~~~~~~~~
key: region
value: category
"""
# SEEDS = {"losangeles": "apa",
#          "sfbay": "apa",
#          "seattle": "apa",
#          "denver": "apa",
#          "austin": "apa",
#          "dallas": "apa",
#          "newyork": "aap"}
SEEDS = {"losangeles": "apa"}


def monitor(workers=8):
    """
    Send searching queries to Craigslist,
    scrape listing URL,
    deduplicate with Redis,
    publish into scrape_listings_task_queue.
    ~~~~~~~~~
    :param workers: number of worker threads

    :return: None
    """
    logger = logging.getLogger(__name__)

    redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)
    cloudamqp_client = CloudAMQPClient(SCRAPE_LISTINGS_TASK_QUEUE_URL,
                                       SCRAPE_LISTINGS_TASK_QUEUE_NAME)

    # while True:
    queue = Queue()
    scrapers = {}

    for region, category in iteritems(SEEDS):
        queue.put({"region": region, "category": category, "start": 0})
        logger.info("Thread task queue add: %s, %s, %s", region, category, 0)

    def scrape_listings():
        while not queue.empty():
            task = queue.get(block=True)

            scraper = scrapers.get(task["region"])
            if scraper is None:
                scraper = ListingScraper(task["region"], task["category"])
                scrapers[task["region"]] = scraper

            num_of_listings = 0
            total_so_far = task["start"]

            for listing in scraper.get_listings(start=task["start"]):
                total_so_far = max(total_so_far, listing["total_so_far"])

                if redis_client.get(listing["url"]) is None:
                    num_of_listings += 1

                    redis_client.set(listing["url"], listing["url"])
                    redis_client.expire(listing["url"], LISTING_TIME_OUT_IN_SECONDS)

                    cloudamqp_client.publish({"listing_url": listing["url"]})

            if total_so_far - task["start"] >= RESULTS_PER_REQUEST:
                task["start"] = total_so_far
                queue.put(task)
                logger.info("Add new task: '%s' to queue", task)
            
            queue.task_done()
            logger.info(" [x] Region=%s, total_processed=%s, published=%s, active_threads=%s",
                        task["region"], total_so_far, num_of_listings, threading.active_count())

    threads = []
    for _ in range(workers):
        thread = threading.Thread(target=scrape_listings)
        thread.start()
        threads.append(thread)

    queue.join()
    logger.info("Queue terminated")
    for thread in threads:
        thread.join()
    logger.info("Threads terminated")

        # cloudamqp_client.sleep(SLEEP_TIME_IN_SECONDS)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s/%(levelname)s/%(name)s/%(message)s",
                        # filename="listing_monitor.log",
                        datefmt="%m-%d/%H:%M:%S",
                        level=logging.INFO)
    monitor(workers=NUM_OF_WORKER_THREADS)
