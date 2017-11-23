# -*- coding: utf-8 -*-

"""housing listing monitor"""

import datetime
import json
import logging
import os
import sys
import threading
import time
try:
    from Queue import Queue  # PY2
except ImportError:
    from queue import Queue  # PY3

import redis
from six import iteritems
from six.moves import range

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "client"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "logger"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scraper"))
from cloudamqp import CloudAMQPClient
from listing import ListingScraper
from default_logger import set_default_dual_logger

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "common", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

REDIS_HOST = CONFIG["redis"]["host"]
REDIS_PORT = CONFIG["redis"]["port"]

MONITOR_SLEEP_TIME_IN_SECONDS = CONFIG["listing"]["monitor"]["sleep_time_in_seconds"]
CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS = CONFIG["cloudamqp"]["client"]["sleep_time_in_seconds"]
LISTING_TIME_OUT_IN_SECONDS = CONFIG["listing"]["time_out_in_seconds"]

SCRAPE_LISTINGS_TASK_QUEUE_URL = CONFIG["cloudamqp"]["scrape_listings_task_queue"]["url"]
SCRAPE_LISTINGS_TASK_QUEUE_NAME = CONFIG["cloudamqp"]["scrape_listings_task_queue"]["name"]

# Craigslist return 120 results per request
RESULTS_PER_REQUEST = CONFIG["craigslist"]["results_per_request"]

NUM_OF_WORKER_THREADS = CONFIG["listing"]["monitor"]["num_of_worker_threads"]

LOG_FILE_NAME = "listing_monitor.log"

# craigslist scraping seeds, {region: category}
SEEDS = CONFIG["craigslist"]["seeds"]


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
    scrapers = {}   # Map region to its scraper

    def scrape_listings():
        """
        Worker task: scrape listings from the seed got from the thread task queue
        Each worker thread has its own cloudamqp_client, newly constructed or got
        from cloudamqp_clients
        """

        cloudamqp_client = cloudamqp_clients.get(threading.current_thread().ident)
        if cloudamqp_client is None:
            cloudamqp_client = CloudAMQPClient(SCRAPE_LISTINGS_TASK_QUEUE_URL,
                                               SCRAPE_LISTINGS_TASK_QUEUE_NAME,
                                               durable=True)
            cloudamqp_clients[threading.current_thread().ident] = cloudamqp_client

        while not queue.empty():
            task = queue.get(block=True)

            scraper = scrapers.get(task["region"])  # getSet scraper
            if scraper is None:
                scraper = ListingScraper(task["region"], task["category"])
                scrapers[task["region"]] = scraper

            num_of_listings_sent = 0
            total_so_far = task["start"]
            logger.info("Thread_%s working on (%s, %s, %s)", threading.current_thread().ident,
                        task["region"], task["category"], task["start"])

            for listing in scraper.get_listings(start=task["start"]):
                total_so_far = max(total_so_far, listing["total_so_far"])

                if redis_client.get(listing["url"]) is None:
                    num_of_listings_sent += 1

                    redis_client.set(listing["url"], listing["url"])
                    redis_client.expire(listing["url"], LISTING_TIME_OUT_IN_SECONDS)

                    cloudamqp_client.publish({"url": listing["url"], "region": listing["region"],
                                              "category": listing["category"]})

            if total_so_far - task["start"] >= RESULTS_PER_REQUEST:
                task["start"] = total_so_far
                queue.put(task)
                logger.info("Thread task queue: add new task: (%s, %s, %s)",
                            task["region"], task["category"], task["start"])

            queue.task_done()
            logger.info(" [x] Region=%s, total_processed=%s, published=%s, active_threads=%s",
                        task["region"], total_so_far,
                        num_of_listings_sent, threading.active_count())

            cloudamqp_client.sleep(CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS)

    while True:
        cloudamqp_clients = {}  # Map thread identification to its cloudamqp_client

        queue = Queue() # Init thread tasks queue
        for region, category in iteritems(SEEDS):
            queue.put({"region": region, "category": category, "start": 0})
            logger.info("Thread task queue: initial add: (%s, %s, %s)", region, category, 0)

        threads = []
        for _ in range(workers):
            thread = threading.Thread(target=scrape_listings)
            thread.start()
            threads.append(thread)

        queue.join()    # Block until all tasks in the queue are completed
        logger.info("Queue terminated")

        for thread in threads:
            thread.join()
        logger.info("Threads terminated")

        for _, client in iteritems(cloudamqp_clients):
            client.close()
        logger.info("CloudAMQP connections are all closed")

        logger.info("%s Sleeping... Next execution: %s",
                    datetime.datetime.now(),
                    datetime.datetime.now() +
                    datetime.timedelta(days=0, seconds=MONITOR_SLEEP_TIME_IN_SECONDS))
        time.sleep(MONITOR_SLEEP_TIME_IN_SECONDS)


if __name__ == "__main__":
    set_default_dual_logger(LOG_FILE_NAME, "a")
    monitor(workers=NUM_OF_WORKER_THREADS)

    # # helper to clear the scrape task queue
    # from cloudamqp import clear_queue
    # clear_queue(SCRAPE_LISTINGS_TASK_QUEUE_URL, SCRAPE_LISTINGS_TASK_QUEUE_NAME)
