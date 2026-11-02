import pika
import pika.exceptions
from retry import retry

from models.order_model import OrderRequest


class OrderSender:
    __QUEUE_NAME = "orders"
    __HOST: str = "rabbitmq"
    __PORT: int = 5672
    __USERNAME: str = "project2"
    __PASSWORD: str = "project2pass"

    def send_order_event(self, order: OrderRequest):
        connection: pika.BlockingConnection = self.__get_connection()
        channel = connection.channel()

        channel.queue_declare(
            queue=self.__QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"}
        )
        channel.basic_publish(
            exchange="",
            routing_key=self.__QUEUE_NAME,
            body=order.model_dump_json(indent=4),
        )

    @retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
    def __get_connection(self) -> pika.BlockingConnection:
        credentials = pika.PlainCredentials(self.__USERNAME, self.__PASSWORD)

        parameters = pika.ConnectionParameters(
            host=self.__HOST, port=self.__PORT, credentials=credentials
        )

        connection = pika.BlockingConnection(parameters)
        return connection
