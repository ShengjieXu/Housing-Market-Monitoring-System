"""basic test for cloudamqp client"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "logger"))
from cloudamqp import CloudAMQPClient
from default_logger import set_default_console_logger

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
with open(CONFIG_FILE) as json_config_file:
    CONFIG = json.load(json_config_file)

QUEUE_URL = CONFIG["cloudamqp"]["scrape_listings_task_queue"]["url"]
QUEUE_NAME = "test"

class CloudAMQPClientTestCase(unittest.TestCase):
    def test_basic(self):
        client = CloudAMQPClient(QUEUE_URL, QUEUE_NAME, durable=True)

        message = {"name": "test", "value": "123"}
        client.publish(message)
        received_message = client.get()

        self.assertEqual(received_message, message)


if __name__ == "__main__":
    set_default_console_logger()
    unittest.main()
