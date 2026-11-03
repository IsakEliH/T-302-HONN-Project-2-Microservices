import json

import pika
import pika.exceptions
from retry import retry


class OrderSender:
    __QUEUE_NAME = "payments"
    __HOST: str = "rabbitmq"
    __PORT: int = 5672


