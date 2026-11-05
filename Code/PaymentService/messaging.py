from models import PaymentResult, PaymentResultInventory

from retry import retry
import pika
import json
EXCHANGE_EMAIL = "email.events.exchange"
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
    - queue: either payments or paymentInventory
    - paymentResult: either for EmailService or InventoryService

    Creates an event and publishes it to the queue
    """

    event = paymentResult.model_dump(mode='json')
    order_id = getattr(paymentResult, "order_id", None) or event.get("orderId")

    # If publishing to the payments queue for the email service, use the consistent hash exchange
    if queue == "payments" and order_id is not None:
        # Ensure the exchange is declared (or declare it in your channel setup)
        channel.exchange_declare(
            exchange=EXCHANGE_EMAIL,
            exchange_type="x-consistent-hash",
            durable=True,
        )

        channel.basic_publish(
            exchange=EXCHANGE_EMAIL,
            routing_key=str(order_id),  # Routes deterministically to the same container instance as OrderCreated
            body=json.dumps(event).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
            mandatory=True,
        )
    else:
        # Fallback for standard direct queues (like paymentInventory)
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