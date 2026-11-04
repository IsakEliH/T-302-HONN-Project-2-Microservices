import json

import pika
import pika.exceptions
from retry import retry

from repositories.inventory_repository import InventoryRepository

QUEUE: str = "paymentInventory"
HOST: str = "rabbitmq"
PORT: int = 5672


def main():
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE, durable=True, arguments={"x-queue-type": "quorum"}
    )

    for method_frame, properties, body in channel.consume(queue=QUEUE):
        if method_frame is None or body is None:
            continue

        # Event is a dictionary with the following keys: orderId, paymentResult
        event = json.loads(body.decode("utf-8"))
        product_id = event.get(
            "productId"
        )  # TODO: Remember to change event from PaymentService to include productId instead of orderId
        payment_result = event.get("paymentResult")

        # TODO: stop reserving the specific product
        if payment_result == "success":
            repository = InventoryRepository()
            repository.decrease_quantity(product_id)
        # if payment_result == "failed":
        #     pass

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)


@retry(pika.exceptions.AMQPConnectionError, tries=3, delay=5, jitter=(1, 3))
def get_connection() -> pika.BlockingConnection:
    parameters = pika.ConnectionParameters(host=HOST, port=PORT)
    return pika.BlockingConnection(parameters)


if __name__ == "__main__":
    main()
