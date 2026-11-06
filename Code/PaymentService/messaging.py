from models import PaymentResult, PaymentResultInventory

from retry import retry
import pika
import json
EMAIL_QUEUE = "email.events"
INVENTORY_QUEUE = "paymentInventory"
QUEUE = "orders"
HOST = "rabbitmq"
PORT = 5672


@retry(pika.exceptions.AMQPConnectionError, tries=3, delay=5, jitter=(1, 3))
def open_chanel():
    """
    Opens the RabbitMQ connection and returns it
    """
    parameters = pika.ConnectionParameters(host=HOST, port=PORT)
    connection = pika.BlockingConnection(parameters)
    return connection


def publish_payment(channel, queue, paymentResult: PaymentResult | PaymentResultInventory):
    """
    Takes in:
    - channel: the RabbitMQ channel
    - queue: either email.events or paymentInventory
    - paymentResult: either for EmailService or InventoryService

    Creates an event and publishes it to the queue
    """

    event = paymentResult.model_dump(mode="json")
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