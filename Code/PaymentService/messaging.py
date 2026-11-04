from models import PaymentResult, PaymentResultInventory

from retry import retry
import pika
import json

QUEUE = "order"
HOST = "rabbitmq"
PORT = 5672


@retry(pika.exceptions.AMQPConnectionError, tries=3, delay=5, jitter=(1, 3))
def open_chanel():
    parameters = pika.ConnectionParameters(
        host=HOST,
        port=PORT,
    )

    connection = pika.BlockingConnection(parameters)
    return connection


def publish_payment(channel, queue, paymentResult: PaymentResult | PaymentResultInventory):
    event = paymentResult.model_dump(mode='json')

    channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=json.dumps(event).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
            mandatory=True,
        )