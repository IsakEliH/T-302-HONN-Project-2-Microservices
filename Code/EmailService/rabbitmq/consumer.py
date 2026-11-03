import json
import logging
import time
from typing import Optional
import pika
import pika.exceptions
from retry import retry

from config import config
from models.event_models import OrderCreatedEvent, PaymentEvent
from services.resend_service import EmailSender

logger = logging.getLogger("EmailService.Consumer")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class RabbitMQConsumer:
    # TODO mitigate using none
    def __init__(self, email_sender: Optional[EmailSender] = None):
        self.email_sender = email_sender or EmailSender()
        self.host = config.RABBITMQ_HOST
        self.port = config.RABBITMQ_PORT
        self.user = config.RABBITMQ_USER
        self.password = config.RABBITMQ_PASSWORD
        self.queues = [q.strip() for q in config.QUEUES if q.strip()]
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self._is_running = False

    @retry(pika.exceptions.AMQPConnectionError, tries=10, delay=3, jitter=(1, 3))
    def _connect(self) -> pika.BlockingConnection:
        logger.info("Connecting to RabbitMQ at %s:%s...", self.host, self.port)
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=60,
            blocked_connection_timeout=300,
        )
        return pika.BlockingConnection(parameters)

    def _setup_channel(self) -> None:
        self.channel = self.connection.channel()
        # prefetch_count=1 ensures worker queue distribution when scaled
        self.channel.basic_qos(prefetch_count=1)

        for queue_name in self.queues:
            try:
                # First attempt quorum queue declaration (as used by OrderService)
                self.channel.queue_declare(
                    queue=queue_name,
                    durable=True,
                    arguments={"x-queue-type": "quorum"},
                )
            except pika.exceptions.ChannelClosedByBroker:
                # If existing queue type is classic, recreate channel and declare without quorum argument
                logger.info("Re-declaring queue '%s' with standard configuration.", queue_name)
                self.channel = self.connection.channel()
                self.channel.basic_qos(prefetch_count=1)
                self.channel.queue_declare(
                    queue=queue_name,
                    durable=True,
                )

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._on_message,
                auto_ack=False,
            )
            logger.info("Subscribed to queue '%s' with prefetch_count=1", queue_name)

    def _on_message(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> None:
        delivery_tag = method.delivery_tag
        routing_key = method.routing_key
        try:
            payload = json.loads(body.decode("utf-8"))
            logger.info("Received event on '%s': %s", routing_key, payload)
            self.process_event(payload, routing_key)
            channel.basic_ack(delivery_tag=delivery_tag)
        except json.JSONDecodeError as err:
            logger.error("Failed to decode JSON from queue '%s': %s", routing_key, err)
            # Ack/discard malformed messages to prevent blocking the queue
            channel.basic_ack(delivery_tag=delivery_tag)
        except Exception as exc:
            logger.error("Error processing message from queue '%s': %s", routing_key, exc, exc_info=True)
            # Ack to avoid poison message loop, or nack without requeue
            channel.basic_ack(delivery_tag=delivery_tag)

    def process_event(self, data: dict, routing_key: str = "") -> None:
        """
        Parses and handles event based on eventType, routing key, or event data.
        """
        event_type = (
            data.get("eventType")
            or data.get("event_type")
            or data.get("type")
            or ""
        ).lower()

        # Check for OrderCreated event
        if (
            "ordercreated" in event_type
            or "order-created" in event_type
            or "order_created" in event_type
            or routing_key == "orders"
            or ("order" in data and "orderId" in data and "status" not in data)
        ):
            # Parse OrderCreatedEvent
            order_event = OrderCreatedEvent.model_validate(data)
            self.email_sender.handle_order_created(order_event)
            return

        # Check for PaymentSuccess event
        if (
            "paymentsuccess" in event_type
            or "payment-success" in event_type
            or "payment_success" in event_type
            or (data.get("status") or "").upper() == "SUCCESS"
        ):
            payment_event = PaymentEvent.model_validate(data)
            self.email_sender.handle_payment_success(payment_event)
            return

        # Check for PaymentFailure event
        if (
            "paymentfailure" in event_type
            or "payment-failure" in event_type
            or "payment_failure" in event_type
            or (data.get("status") or "").upper() in ("FAILURE", "FAILED")
        ):
            payment_event = PaymentEvent.model_validate(data)
            self.email_sender.handle_payment_failure(payment_event)
            return

        logger.warning("Unrecognized event structure received: %s", data)

    def start(self) -> None:
        self._is_running = True
        while self._is_running:
            try:
                self.connection = self._connect()
                self._setup_channel()
                logger.info("EmailService consumer started and waiting for messages...")
                self.channel.start_consuming()
            except (pika.exceptions.AMQPConnectionError, pika.exceptions.ConnectionClosedByBroker) as exc:
                logger.warning("RabbitMQ connection lost (%s). Reconnecting in 5 seconds...", exc)
                time.sleep(5)
            except pika.exceptions.AMQPError as exc:
                logger.error("RabbitMQ AMQP error: %s. Reconnecting in 5 seconds...", exc)
                time.sleep(5)
            except Exception as exc:
                logger.error("Unexpected error in consumer loop: %s", exc, exc_info=True)
                if not self._is_running:
                    break
                time.sleep(5)

    def stop(self) -> None:
        logger.info("Stopping EmailService consumer...")
        self._is_running = False
        if self.channel and self.channel.is_open:
            try:
                self.channel.stop_consuming()
            except Exception:
                pass
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception:
                pass
        logger.info("EmailService consumer stopped.")
