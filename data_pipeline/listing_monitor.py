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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "logger"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scraper"))

import redis
from six import iteritems
from six.moves import range

from cloudamqp import CloudAMQPClient
from cl_listing_scraper import ListingScraper
from default_logger import set_default_dual_logger

REDIS_HOST = "localhost"
REDIS_PORT = 6379

SLEEP_TIME_IN_SECONDS = 10
LISTING_TIME_OUT_IN_SECONDS = 3600 * 24 * 3

SCRAPE_LISTINGS_TASK_QUEUE_URL = "amqp://zsjdmkfu:x1LwP5IRoZjs7C1LWpMK7_87OdxLoQnM@donkey.rmq.cloudamqp.com/zsjdmkfu"
SCRAPE_LISTINGS_TASK_QUEUE_NAME = "hmms-scrape-listings-task-queue"

# Craigslist return 120 results per request
RESULTS_PER_REQUEST = 120

NUM_OF_WORKER_THREADS = 8

LOG_FILE_NAME = "listing_monitor.log"

# craigslist scraping seeds, {region: category}
SEEDS = {"losangeles": "apa",
         "sfbay": "apa",
         "seattle": "apa",
         "denver": "apa",
         "austin": "apa",
         "dallas": "apa",
         "newyork": "aap"}


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
    queue = Queue()
    scrapers = {}
    scrape_task_sent_count = 0

    # TODO: while True:
    # Map thread identification to its cloudamqp_client
    cloudamqp_clients = {}

    for region, category in iteritems(SEEDS):
        queue.put({"region": region, "category": category, "start": 0})
        logger.info("Thread task queue: initial add: (%s, %s, %s)", region, category, 0)

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

            scraper = scrapers.get(task["region"])
            if scraper is None:
                scraper = ListingScraper(task["region"], task["category"])
                scrapers[task["region"]] = scraper

            num_of_listings = 0
            total_so_far = task["start"]
            logger.info("Thread_%s working on (%s, %s, %s)", threading.current_thread().ident,
                        task["region"], task["category"], task["start"])

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
                logger.info("Thread task queue: add new task: (%s, %s, %s)",
                            task["region"], task["category"], task["start"])
            
            queue.task_done()
            logger.info(" [x] Region=%s, total_processed=%s, published=%s, active_threads=%s",
                        task["region"], total_so_far, num_of_listings, threading.active_count())
            scrape_task_sent_count += num_of_listings
            
            cloudamqp_client.sleep(SLEEP_TIME_IN_SECONDS)

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

    for _, client in iteritems(cloudamqp_clients):
        client.close()
    logger.info("CloudAMQP connections are all closed")
    logger.info("Scrape task sent=%s", scrape_task_sent_count)


if __name__ == "__main__":
    set_default_dual_logger(LOG_FILE_NAME, "a")
    monitor(workers=NUM_OF_WORKER_THREADS)

    # # helper to clear the scrape task queue
    # from cloudamqp import clear_queue
    # clear_queue(SCRAPE_LISTINGS_TASK_QUEUE_URL, SCRAPE_LISTINGS_TASK_QUEUE_NAME)
