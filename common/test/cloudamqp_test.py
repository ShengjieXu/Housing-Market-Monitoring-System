"""basic test for cloudamqp client"""

import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "logger"))

from cloudamqp import CloudAMQPClient
from default_logger import set_default_console_logger


QUEUE_URL = "amqp://zsjdmkfu:x1LwP5IRoZjs7C1LWpMK7_87OdxLoQnM@donkey.rmq.cloudamqp.com/zsjdmkfu"
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
