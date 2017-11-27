# -*- coding: utf-8 -*-

"""Fetch listing details from the detail page"""

import datetime
import json
import logging
import os
import pprint
import sys
import threading
import time

from six import iteritems
from six.moves import range

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "client"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common", "logger"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scraper"))
from cloudamqp import CloudAMQPClient
from default_logger import set_default_dual_logger
from detail import DetailScraper

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "common", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

SCRAPE_LISTINGS_TASK_QUEUE_URL = CONFIG["cloudamqp"]["scrape_listings_task_queue"]["url"]
SCRAPE_LISTINGS_TASK_QUEUE_NAME = CONFIG["cloudamqp"]["scrape_listings_task_queue"]["name"]

DEDUPE_LISTINGS_TASK_QUEUE_URL = CONFIG["cloudamqp"]["dedupe_listings_task_queue"]["url"]
DEDUPE_LISTINGS_TASK_QUEUE_NAME = CONFIG["cloudamqp"]["dedupe_listings_task_queue"]["name"]

FETCHER_SLEEP_TIME_IN_SECONDS = CONFIG["listing"]["fetcher"]["sleep_time_in_seconds"]
CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS = CONFIG["listing"]["fetcher"]["interval_in_seconds"]

NUM_OF_WORKER_THREADS = CONFIG["listing"]["fetcher"]["num_of_worker_threads"]

LOG_FILE_NAME = "listing_fetcher.log"


def _get_and_set_client(cloudamqp_clients, queue_url, queue_name, durable=True):
    """get current thread's client from existing client dict"""

    cloudamqp_client = cloudamqp_clients.get(threading.current_thread().ident)
    if cloudamqp_client is None:
        cloudamqp_client = CloudAMQPClient(queue_url, queue_name, durable=durable)
        cloudamqp_clients[threading.current_thread().ident] = cloudamqp_client
    return cloudamqp_client


def fetch(workers=8):
    """
    1. Each worker fetches scrape task from scrape_listings_tasks_queue
    2. Scrape the content page
    3. Send results into dedupe_listings_task_queue
    """

    logger = logging.getLogger(__name__)

    def scrape_details():
        """
        Worker task:
        1. get task from queue
        2. scrape details
        """

        cloudamqp_receiver_client, cloudamqp_sender_client = None, None

        while True:
            if cloudamqp_receiver_client and cloudamqp_sender_client:
                task = cloudamqp_receiver_client.get()

                if task:
                    try:
                        logger.info("Thread_%s working on (%s, %s, %s), active_threads_count=%s",
                            threading.current_thread().ident, task["url"], task["region"], task["category"],
                            threading.active_count())
                        scraper = DetailScraper(url=task["url"], region=task["region"], category=task["category"])
                        details = scraper.get_details()
                        if details is not None:
                            cloudamqp_sender_client.publish(details, durable=True)
                    except (SystemExit, KeyboardInterrupt):
                        raise
                    except Exception as e:
                        logger.error("Failed to handle task=%s", pprint.pformat(task), exc_info=True)
                else:
                    logger.info("No more tasks. Thread=%s exiting...", threading.current_thread().ident)
                    break

                cloudamqp_receiver_client.sleep(CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS)
                cloudamqp_sender_client.sleep(CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS)
            else:
                cloudamqp_receiver_client = _get_and_set_client(
                    cloudamqp_receiver_clients, SCRAPE_LISTINGS_TASK_QUEUE_URL,
                    SCRAPE_LISTINGS_TASK_QUEUE_NAME, durable=True)
                cloudamqp_sender_client = _get_and_set_client(
                    cloudamqp_sender_clients, DEDUPE_LISTINGS_TASK_QUEUE_URL,
                    DEDUPE_LISTINGS_TASK_QUEUE_NAME, durable=True)
                logger.info("Receiver and sender queues connenction established")

    while True:
        # Map thread identification to its cloudamqp_[receiver,sender]_client
        cloudamqp_receiver_clients = {}
        cloudamqp_sender_clients = {}

        threads = []
        for _ in range(workers):
            thread = threading.Thread(target=scrape_details)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
        logger.info("Threads terminated")

        for clients in (cloudamqp_receiver_clients, cloudamqp_sender_clients):
            for _, client in iteritems(clients):
                client.close()
        logger.info("CloudAMQP connections are all closed")

        logger.info("%s Listing Fetcher goes sleeping... Next execution: %s",
                    datetime.datetime.now(),
                    datetime.datetime.now() +
                    datetime.timedelta(days=0, seconds=FETCHER_SLEEP_TIME_IN_SECONDS))
        time.sleep(FETCHER_SLEEP_TIME_IN_SECONDS)

if __name__ == "__main__":
    set_default_dual_logger(LOG_FILE_NAME, "a")
    fetch(workers=NUM_OF_WORKER_THREADS)

    # # helper to clear the scrape task queue
    # from cloudamqp import clear_queue
    # clear_queue(DEDUPE_LISTINGS_TASK_QUEUE_URL, DEDUPE_LISTINGS_TASK_QUEUE_NAME)
