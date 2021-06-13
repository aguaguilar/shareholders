import os

import pika


class Amqp:
    """
    Abstraction to interact with amqp broker.
    """
    def __init__(self, exchange="shares", exchange_type="fanout"):
        credentials = pika.PlainCredentials(os.getenv("RABBITMQ_USER"), os.getenv("RABBITMQ_PASSWORD"))
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.getenv("AMQP_HOST"), credentials=credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)

    def publish(self, message, exchange="shares", routing_key=""):
        self.channel.basic_publish(exchange, routing_key, body=message)

    def close_connection(self):
        self.connection.close()

    def start_consuming(self, callback, queue='', exchange="shares"):
        result = self.channel.queue_declare(queue=queue, exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange, queue=queue_name)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        self.channel.start_consuming()
