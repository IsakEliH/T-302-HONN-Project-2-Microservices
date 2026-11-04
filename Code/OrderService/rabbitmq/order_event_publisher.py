import json

import pika
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel
from retry import retry

from models.order_model import OrderRequest, build_order_email_request


class OrderSender:
    __QUEUE_ORDER: str = "orders"
    __QUEUE_EMAIL: str = "order_email"
    __queues: list[str] = [__QUEUE_ORDER, __QUEUE_EMAIL]

    __EVENT_TYPE: str = "OrderCreated"

    __HOST: str = "rabbitmq"
    __PORT: int = 5672

    def send_order_event(self, order: OrderRequest, order_id: int):
        connection: pika.BlockingConnection = self.__get_connection()

        try:
            channel = self.__create_channel(connection, self.__queues)

            # Publish to payment queue
            payment_order_event_body = self.__create_order_event_body(
                self.__EVENT_TYPE, order_id, order
            )
            self.__publish_to_queue(
                channel, self.__QUEUE_ORDER, payment_order_event_body
            )

            # Publish to email queue
            email_order_model = build_order_email_request(order, order_id)
            email_order_event_body = self.__create_order_event_body(
                self.__EVENT_TYPE, order_id, email_order_model
            )
            self.__publish_to_queue(channel, self.__QUEUE_EMAIL, email_order_event_body)

        finally:
            if connection.is_open:
                connection.close()

    def __create_order_event_body(
        self, event_type: str, order_id: int, order_model
    ) -> bytes:
        order_event = {
            "eventType": event_type,
            "orderId": order_id,
            "order": order_model.model_dump(mode="json")
        }
        return json.dumps(order_event).encode("utf-8")

    def __create_channel(self, connection: pika.BlockingConnection, queues: list[str]):
        channel = connection.channel()
        # Declare all queues
        for queue in queues:
            channel.queue_declare(
                queue=queue,
                durable=True,
                arguments={"x-queue-type": "quorum"},
            )
        channel.confirm_delivery()
        return channel

    def __publish_to_queue(self, channel: BlockingChannel, queue: str, body: bytes):
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )

    @retry(pika.exceptions.AMQPConnectionError, tries=3, delay=5, jitter=(1, 3))
    def __get_connection(self) -> pika.BlockingConnection:
        parameters = pika.ConnectionParameters(host=self.__HOST, port=self.__PORT)
        return pika.BlockingConnection(parameters)
