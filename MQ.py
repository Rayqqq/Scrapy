import pika
import logging


class MQ(object):
    def __init__(self, usage, exchange=None, routing_key=None, host=None, port=None, user=None, passwd=None):
        if user and passwd:
            credentials = pika.PlainCredentials(user, passwd)
        else:
            credentials = None
        self._exchange = exchange
        self._routing_key = routing_key
        if (not exchange) and (not routing_key):
            raise
        if usage == 'Task':
            if not self._routing_key:
                raise
        elif usage == 'PubSub':
            if not self._exchange:
                raise
        elif usage == 'Routing':
            if (not self._exchange) or (not self._routing_key):
                raise
        else:
            raise
        if credentials:
            self._connection = pika.BlockingConnection(pika.ConnectionParameters(credentials=credentials,
                                                                                 host=host, port=port))
        else:
            self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))

        self._channel = self._connection.channel()
        self._usage_dict = {
            'Task': {
                'pub': self._task_pub,
                'sub': self._task_sub
            },
            'PubSub': {
                'pub': self._pub_sub_pub,
                'sub': self._pub_sub_sub
            },
            'Routing': {
                'pub': self._routing_pub,
                'sub': self._routing_sub
            }
        }
        self.pub = self._usage_dict[usage]['pub']
        self.sub = self._usage_dict[usage]['sub']

    def __del__(self):
        if self._connection:
            self._connection.close()

    def _task_pub(self, msg):
        if isinstance(self._routing_key, str):
            self._channel.queue_declare(queue=self._routing_key)
            self._channel.basic_publish(exchange='', routing_key=self._routing_key)
        elif isinstance(self._routing_key, list):
            for key in self._routing_key:
                self._channel.queue_declare(queue=key)
                self._channel.basic_publish(exchange='', routing_key=key, body=msg)

    def _task_sub(self, callback):
        if isinstance(self._routing_key, str):
            self._channel.queue_declare(queue=self._routing_key)
            self._channel.basic_consume(callback, queue=self._routing_key)
        if isinstance(self._routing_key, list):
            for key in self._routing_key:
                self._channel.queue_declare(queue=key)
                self._channel.basic_consume(callback, queue=key)
        self._channel.start_consuming()

    def _pub_sub_pub(self, msg):
        self._channel.exchange_declare(exchange=self._exchange, type='fanout')
        self._channel.basic_publish(exchange=self._exchange, routing_key='', body=msg)

    def _pub_sub_sub(self, callback):
        self._channel.exchange_declare(exchange=self._exchange, type='fanout')
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=self._exchange, queue=queue_name)
        self._channel.basic_consume(callback, queue=queue_name, no_ack=True)
        self._channel.start_consuming()

    def _routing_pub(self, msg):
        self._channel.exchange_declare(exchange=self._exchange, type='direct')
        if isinstance(self._routing_key, str):
            self._channel.basic_publish(exchange=self._exchange, routing_key=self._routing_key, body=msg)
        if isinstance(self._routing_key, list):
            for key in self._routing_key:
                self._channel.basic_publish(exchange=self._exchange, routing_key=key, body=msg)

    def _routing_sub(self, callback):
        self._channel.exchange_declare(exchange=self._exchange, type='direct')
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        if isinstance(self._routing_key, str):
            self._channel.queue_bind(exchange=self._exchange, queue=queue_name, routing_key=self._routing_key)
        if isinstance(self._routing_key, list):
            for key in self._routing_key:
                self._channel.queue_bind(exchange=self._exchange, queue=queue_name, routing_key=key)
        self._channel.basic_consume(callback, queue=queue_name, no_ack=True)
        self._channel.start_consuming()
