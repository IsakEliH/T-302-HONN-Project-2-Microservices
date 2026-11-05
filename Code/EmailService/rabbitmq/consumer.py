import json
import logging
import socket
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
    def __init__(self, email_sender: Optional[EmailSender] = None):
        self.email_sender = email_sender or EmailSender()
        self.host = config.RABBITMQ_HOST
        self.port = config.RABBITMQ_PORT
        self.user = config.RABBITMQ_USER
        self.password = config.RABBITMQ_PASSWORD
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self._is_running = False

        # In-memory stores to track and correlate asynchronous OrderCreated and Payment events by order_id
        self.orders: dict[int, OrderCreatedEvent] = {}
        self.pending_payments: dict[int, list[PaymentEvent]] = {}

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
        self.channel.basic_qos(prefetch_count=1)

        # 1. Setup Consistent Hash Exchange and Dynamic Queue for Email Events
        email_exchange = "email.events.exchange"
        container_hostname = socket.gethostname()
        dynamic_email_queue = f"email_queue_{container_hostname}"

        self.channel.exchange_declare(
            exchange=email_exchange,
            exchange_type="x-consistent-hash",
            durable=True,
        )

        # Declare a unique private queue for this container instance
        self.channel.queue_declare(
            queue=dynamic_email_queue,
            durable=True,
            exclusive=False,  # Keep durable so messages aren't lost if restarting briefly
        )

        # Bind this container's queue to the exchange with weight '1'
        self.channel.queue_bind(
            exchange=email_exchange,
            queue=dynamic_email_queue,
            routing_key="1",
        )

        self.channel.basic_consume(
            queue=dynamic_email_queue,
            on_message_callback=self._on_message,
            auto_ack=False,
        )
        logger.info("Subscribed to dynamic email queue '%s' via consistent hash exchange", dynamic_email_queue)

        # 2. Setup standard queue for Payment events (e.g., 'payments')
        payment_queue = "payments"
        try:
            self.channel.queue_declare(
                queue=payment_queue,
                durable=True,
                arguments={"x-queue-type": "quorum"},
            )
        except pika.exceptions.ChannelClosedByBroker:
            logger.info("Re-declaring queue '%s' with standard configuration.", payment_queue)
            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=1)
            self.channel.queue_declare(
                queue=payment_queue,
                durable=True,
            )

        self.channel.basic_consume(
            queue=payment_queue,
            on_message_callback=self._on_message,
            auto_ack=False,
        )
        logger.info("Subscribed to queue '%s' with prefetch_count=1", payment_queue)

    def _on_message(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> None:
        delivery_tag = method.delivery_tag
        routing_key = method.routing_key
        time.sleep(0.5)
        try:
            payload = json.loads(body.decode("utf-8"))
            logger.info("Received event (routing_key/queue: %s): %s", routing_key, payload)
            self.process_event(payload, routing_key)
            channel.basic_ack(delivery_tag=delivery_tag)
        except json.JSONDecodeError as err:
            logger.error("Failed to decode JSON: %s", err)
            channel.basic_ack(delivery_tag=delivery_tag)
        except Exception as exc:
            logger.error("Error processing message: %s", exc, exc_info=True)
            channel.basic_ack(delivery_tag=delivery_tag)

    def _handle_order_created(self, order_event: OrderCreatedEvent) -> None:
        order_id = order_event.order_id
        self.orders[order_id] = order_event
        logger.info(
            "Stored OrderCreated record for order %s (buyer: %s, merchant: %s)",
            order_id,
            order_event.buyer_email,
            order_event.merchant_email,
        )

        self.email_sender.handle_order_created(order_event)

        if order_id in self.pending_payments:
            pending_list = self.pending_payments.pop(order_id)
            logger.info(
                "Found %s pending payment event(s) for order %s. Sending correlated payment emails now.",
                len(pending_list),
                order_id,
            )
            for payment_event in pending_list:
                self._dispatch_payment_email(
                    payment_event,
                    buyer_email=order_event.buyer_email,
                    merchant_email=order_event.merchant_email,
                )

    def _handle_payment_event(self, payment_event: PaymentEvent) -> None:
        order_id = payment_event.order_id
        if order_id in self.orders:
            order_info = self.orders[order_id]
            buyer_email = order_info.buyer_email or payment_event.buyer_email
            merchant_email = order_info.merchant_email or payment_event.merchant_email
            logger.info("Correlated payment event for order %s with stored order emails.", order_id)
            self._dispatch_payment_email(
                payment_event,
                buyer_email=buyer_email,
                merchant_email=merchant_email,
            )
        else:
            self.pending_payments.setdefault(order_id, []).append(payment_event)
            logger.info(
                "OrderCreated for order %s not yet received. Stored payment event in pending queue.",
                order_id,
            )

    def _dispatch_payment_email(
        self,
        payment_event: PaymentEvent,
        buyer_email: Optional[str] = None,
        merchant_email: Optional[str] = None,
    ) -> None:
        if payment_event.is_success:
            self.email_sender.handle_payment_success(
                payment_event,
                buyer_email=buyer_email,
                merchant_email=merchant_email,
            )
        else:
            self.email_sender.handle_payment_failure(
                payment_event,
                buyer_email=buyer_email,
                merchant_email=merchant_email,
            )

    def process_event(self, data: dict, routing_key: str = "") -> None:
        event_type = (
            data.get("eventType")
            or data.get("event_type")
            or data.get("type")
            or ""
        ).lower()

        is_order_created = (
            "ordercreated" in event_type
            or "order-created" in event_type
            or "order_created" in event_type
            or ("order" in data and "orderId" in data)
            or ("buyer_email" in data or "buyerEmail" in data)
            or ("product_name" in data or "productName" in data)
            or ("total_price" in data or "totalPrice" in data)
        )

        if is_order_created:
            order_event = OrderCreatedEvent.model_validate(data)
            self._handle_order_created(order_event)
            return

        is_payment = (
            "payment" in event_type
            or routing_key == "payments"
            or "paymentResult" in data
            or "payment_result" in data
            or ("orderId" in data and "status" in data and "product_name" not in data and "productName" not in data and "buyerEmail" not in data and "buyer_email" not in data)
        )

        if is_payment:
            payment_event = PaymentEvent.model_validate(data)
            self._handle_payment_event(payment_event)
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