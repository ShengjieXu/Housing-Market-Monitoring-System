# -*- coding: utf-8 -*-

"""Fetch listing details from the detail page"""

import json
import logging
import os
import pprint
import sys
import threading
import time

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

CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS = CONFIG["listing"]["fetcher"]["interval_in_seconds"]

NUM_OF_WORKER_THREADS = CONFIG["listing"]["fetcher"]["num_of_worker_threads"]

LOG_FILE_NAME = "listing_fetcher.log"


def _scrape_details(run_event):
    """
    Worker task:
    1. get task from queue
    2. scrape details
    """

    logger = logging.getLogger(__name__)
    cloudamqp_receiver_client, cloudamqp_sender_client = None, None

    while run_event.is_set():
        if cloudamqp_receiver_client and cloudamqp_sender_client:
            task = cloudamqp_receiver_client.get()

            if task:
                try:
                    logger.info("Thread_%s working on (%s, %s, %s), active_threads_count=%s",
                                threading.current_thread().ident,
                                task["url"], task["region"], task["category"],
                                threading.active_count())
                    scraper = DetailScraper(url=task["url"],
                                            region=task["region"],
                                            category=task["category"])
                    details = scraper.get_details()
                    if details is not None:
                        cloudamqp_sender_client.publish(details, durable=True)
                except Exception:
                    logger.error("Failed to handle task=%s", pprint.pformat(task), exc_info=True)

            cloudamqp_receiver_client.sleep(CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS)
            cloudamqp_sender_client.sleep(CLOUDAMQP_CLIENT_SLEEP_TIME_IN_SECONDS)
        else:
            cloudamqp_receiver_client = CloudAMQPClient(SCRAPE_LISTINGS_TASK_QUEUE_URL,
                                                        SCRAPE_LISTINGS_TASK_QUEUE_NAME,
                                                        durable=True)
            cloudamqp_sender_client = CloudAMQPClient(DEDUPE_LISTINGS_TASK_QUEUE_URL,
                                                      DEDUPE_LISTINGS_TASK_QUEUE_NAME,
                                                      durable=True)
            logger.debug("Receiver and sender queues connenction established")

    if cloudamqp_receiver_client:
        cloudamqp_receiver_client.close()
    if cloudamqp_sender_client:
        cloudamqp_sender_client.close()
    logger.debug("Receiver and sender queues connenction closed")


def fetch(workers=8):
    """
    1. Each worker fetches scrape task from scrape_listings_tasks_queue
    2. Scrape the content page
    3. Send results into dedupe_listings_task_queue
    """

    logger = logging.getLogger(__name__)

    run_event = threading.Event()
    run_event.set()

    threads = []
    for _ in range(workers):
        thread = threading.Thread(target=_scrape_details, args=(run_event,))
        thread.start()
        threads.append(thread)

    try:
        while True:
            time.sleep(.1)
    except (SystemExit, KeyboardInterrupt):
        logger.info("Attemped exit. Terminating %s threads...", threading.active_count())
        run_event.clear()

    for thread in threads:
        thread.join()
    logger.info("Threads terminated")

    logger.info("Fetcher exited")


if __name__ == "__main__":
    set_default_dual_logger(LOG_FILE_NAME)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("chardet").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    fetch(workers=NUM_OF_WORKER_THREADS)
