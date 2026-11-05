import json
import logging

import pika
import pika.exceptions
from repositories.inventory_repository import InventoryRepository
from retry import retry

logger = logging.getLogger("InventoryService.Consumer")


class InventoryConsumer:
    QUEUE: str = "paymentInventory"
    HOST: str = "rabbitmq"
    PORT: int = 5672

    def __init__(self) -> None:
        self.connection = None
        self.channel = None

    def start_consuming(self) -> None:
        logger.info("Starting InventoryConsumer...")
        try:
            self.connection = self._get_connection()
            self.channel = self.connection.channel()

            self.channel.queue_declare(
                queue=self.QUEUE, durable=True, arguments={"x-queue-type": "quorum"}
            )

            self.channel.basic_qos(prefetch_count=1)

            self.channel.basic_consume(
                queue=self.QUEUE,
                on_message_callback=self._process_message,
                auto_ack=False,
            )

            logger.info("Subscribed to queue '%s'", self.QUEUE)
            self.channel.start_consuming()

        except pika.exceptions.AMQPError:
            logger.exception("RabbitMQ consumer error")

        finally:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("RabbitMQ connection closed.")

    def stop_consuming(self) -> None:
        if self.connection and self.connection.is_open:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()

    def _process_message(self, channel, method, properties, body):
        event = json.loads(body.decode("utf-8"))

        product_id = event.get("productId")
        payment_result = event.get("paymentResult")

        # TODO: stop reserving the specific product
        if payment_result == "success":
            repository = InventoryRepository()
            repository.decrease_quantity(product_id)

            logger.info("Decreased quantity for productID: %s", product_id)

        channel.basic_ack(delivery_tag=method.delivery_tag)

    @retry(pika.exceptions.AMQPConnectionError, tries=3, delay=5, jitter=(1, 3))
    def _get_connection(self) -> pika.BlockingConnection:
        logger.info("Connecting to RabbitMQ at %s:%s...", self.HOST, self.PORT)
        parameters = pika.ConnectionParameters(host=self.HOST, port=self.PORT)
        return pika.BlockingConnection(parameters)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = InventoryConsumer()
    consumer.start_consuming()
