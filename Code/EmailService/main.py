import logging
import signal
import sys

from rabbitmq.consumer import RabbitMQConsumer
from services.resend_service import EmailSender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("EmailService")


def main():
    logger.info("Initializing EmailService with Resend API...")
    email_sender = EmailSender()
    consumer = RabbitMQConsumer(email_sender=email_sender)

    def signal_handler(sig, frame):
        logger.info("Termination signal received. Shutting down EmailService...")
        consumer.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting RabbitMQ Consumer loop...")
    consumer.start()


if __name__ == "__main__":
    main()
