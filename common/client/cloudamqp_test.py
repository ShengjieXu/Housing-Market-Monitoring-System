"""basic test for cloudamqp client"""

from cloudamqp import CloudAMQPClient
import logging

QUEUE_URL = "amqp://zsjdmkfu:x1LwP5IRoZjs7C1LWpMK7_87OdxLoQnM@donkey.rmq.cloudamqp.com/zsjdmkfu"
QUEUE_NAME = "test"

def test_basic():
    """smoke test"""
    client = CloudAMQPClient(QUEUE_URL, QUEUE_NAME)

    message = {"name": "test", "value": "123"}
    client.publish(message)
    received_message = client.get()
    assert received_message == message

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Test started")
    test_basic()
    logger.info("Test passed")
