"""A CloudAMQP client"""

import json
import logging
import pika

class CloudAMQPClient(object):
    """CloudAMQP client class"""

    def __init__(self, queue_url, queue_name):
        self.logger = logging.getLogger(__name__)
        self.queue_url = queue_url
        self.queue_name = queue_name
        self.params = pika.URLParameters(queue_url)
        self.params.socket_timeout = 5
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel() # start a channel
        self.channel.queue_declare(queue=queue_name) # Declare a queue
        self.logger.debug("CloudAMQP: queue_name=%s, queue_url=%s initialized",
                          queue_name, queue_url)

    def publish(self, message):
        """publish message"""
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message))
        self.logger.info(" [x] Sent %s to %s", message, self.queue_name)

    def get(self):
        """get message"""
        method_frame, _, body = self.channel.basic_get(self.queue_name)
        if method_frame:
            self.logger.info(" [x] Received message from %s: %s", self.queue_name, body)
            self.channel.basic_ack(method_frame.delivery_tag)
            return json.loads(body)
        self.logger.info("No message returned from %s", self.queue_name)
        return None

    def sleep(self, seconds):
        """BlockingConnection.sleep is a safer way to sleep than time.sleep(). This
        will repond to server's heartbeat."""
        self.connection.sleep(seconds)
