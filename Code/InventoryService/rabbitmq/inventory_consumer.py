import json

import pika
import pika.exceptions
from repositories.inventory_repository import InventoryRepository
from retry import retry

QUEUE: str = "paymentInventory"
HOST: str = "rabbitmq"
PORT: int = 5672


def main():
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE, durable=True, arguments={"x-queue-type": "quorum"}
    )

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=QUEUE,
        on_message_callback=process_message,
        auto_ack=False,
    )

    channel.start_consuming()


def process_message(channel, method, properties, body):
    event = json.loads(body.decode("utf-8"))

    product_id = event.get("productId")
    payment_result = event.get("paymentResult")

    # TODO: stop reserving the specific product
    if payment_result == "success":
        repository = InventoryRepository()
        repository.decrease_quantity(product_id)

    channel.basic_ack(delivery_tag=method.delivery_tag)


@retry(pika.exceptions.AMQPConnectionError, tries=3, delay=5, jitter=(1, 3))
def get_connection() -> pika.BlockingConnection:
    parameters = pika.ConnectionParameters(host=HOST, port=PORT)
    return pika.BlockingConnection(parameters)


if __name__ == "__main__":
    main()
