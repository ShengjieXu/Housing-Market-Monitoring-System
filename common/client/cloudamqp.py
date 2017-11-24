# -*- coding: utf-8 -*-

"""A CloudAMQP client"""

import json
import logging
import pika

class CloudAMQPClient(object):
    """CloudAMQP client class"""

    def __init__(self, queue_url, queue_name, durable=True):
        self.logger = logging.getLogger(__name__)
        self.queue_url = queue_url
        self.queue_name = queue_name
        self.params = pika.URLParameters(queue_url)
        self.params.socket_timeout = 5
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel() # start a channel
        self.channel.queue_declare(queue=queue_name, durable=durable) # Declare a queue
        self.channel.basic_qos(prefetch_count=1) # qos: deliver <= 1 message to each client
        self.logger.debug("CloudAMQP: queue_name=%s, queue_url=%s initialized",
                          queue_name, queue_url)

    def publish(self, message, durable=True):
        """publish message"""
        if durable:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                ))
        else:
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
    
    def close(self):
        """close the connection"""
        self.connection.close()


def clear_queue(queue_url, queue_name, durable=True):
    """clear the contents of the queue by sending get requests"""
    logger = logging.getLogger(__name__)
    client = CloudAMQPClient(queue_url, queue_name, durable)

    num_of_messages = 0

    while True:
        if client is not None:
            msg = client.get()
            if msg is None:
                logger.info("Cleared %d messages.", num_of_messages)
                return
            num_of_messages += 1

    client.close()
