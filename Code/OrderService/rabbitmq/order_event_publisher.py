import json

import pika
import pika.exceptions
from retry import retry

from models.order_model import OrderRequest


class OrderSender:
    __QUEUE_NAME = "orders"
    __HOST: str = "rabbitmq"
    __PORT: int = 5672

    def send_order_event(self, order: OrderRequest, order_id: int):
        connection: pika.BlockingConnection = self.__get_connection()
        channel = connection.channel()

        try:
            channel.queue_declare(
                queue=self.__QUEUE_NAME,
                durable=True,
                arguments={"x-queue-type": "quorum"},
            )

            channel.confirm_delivery()

            event = {
                "eventType": "OrderCreated",
                "orderId": order_id,
                "order": order.model_dump(mode="json"),
            }

            channel.basic_publish(
                exchange="",
                routing_key=self.__QUEUE_NAME,
                body=json.dumps(event).encode("utf-8"),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
                mandatory=True,
            )
        finally:
            if connection.is_open:
                connection.close()

    @retry(pika.exceptions.AMQPConnectionError, tries=3, delay=5, jitter=(1, 3))
    def __get_connection(self) -> pika.BlockingConnection:

        parameters = pika.ConnectionParameters(host=self.__HOST, port=self.__PORT)
        connection = pika.BlockingConnection(parameters)
        return connection
