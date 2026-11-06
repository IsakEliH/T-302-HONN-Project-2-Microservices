from card_validation import validateCard
from models import PaymentResult, PaymentResultInventory
from messaging import (
    EMAIL_QUEUE,
    INVENTORY_QUEUE,
    QUEUE,
    open_chanel,
    publish_payment,
)
from payment_repository import PaymentRepository

import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("PaymentService")


def save_payment(orderId: int, status: str):
    repository = PaymentRepository()
    repository.save_payment(orderId, status)



def main():
    """
    - Opens up a channel and for loops through the QUEUE, so if a new event is sent it is processed
    - Checks the validation of the card info
    - Saves the orderId and the status of the validation
    - Creates a PaymentResult object
    - Sends the object to be sent as an event
    """

    logger.info("Initializing PaymentService...")

    try:
        # Connect to RabbitMQ
        logger.info("Connecting to RabbitMQ...")
        connection = open_chanel()
        channel = connection.channel()

        logger.info("Successfully connected to RabbitMQ.")

        # Declare queue
        for queue in (QUEUE, EMAIL_QUEUE, INVENTORY_QUEUE):
            logger.info("Declaring queue '%s'...", queue)
            channel.queue_declare(
                queue=queue,
                durable=True,
                arguments={"x-queue-type": "quorum"},
            )
            logger.info("Successfully declared queue '%s'.", queue)

        channel.confirm_delivery()
        logger.info("Starting PaymentService consumer...")



        for method, _properties, body in channel.consume(QUEUE):

            event = json.loads(body.decode("utf-8"))
            orderId = event["orderId"]
            order = event["order"]
            logger.info("Received order event. Order ID: %s", orderId)


            if validateCard(order.get("creditCard")):
                status = "success"
            else:
                status = "failed"
            logger.info("Payment validation completed. Order ID: %s, Status: %s", orderId, status)

            save_payment(orderId, status)

            logger.info("Payment saved. Order ID: %s", orderId)

            # result for Email
            result = PaymentResult(
                orderId=orderId,
                paymentResult=status,
                buyerEmail=order.get("buyerEmail"),
                merchantEmail=order.get("merchantEmail"),
            )

            # result for Inventory
            resultInventory = PaymentResultInventory(
                productId=order.get("productId"),
                paymentResult=status
            )
            

            # Sends queue to EmailService
            publish_payment(channel, EMAIL_QUEUE, result)
            logger.info("Published payment result to EmailService through queue '%s'.", EMAIL_QUEUE)

            # Sends queue to InventoryService
            publish_payment(channel, INVENTORY_QUEUE, resultInventory)
            logger.info("Published payment result to InventoryService through, Queue: 'paymentInventory'.")

            channel.basic_ack(method.delivery_tag)

            logger.info("Successfully processed order %s.", orderId)


    except Exception:
        logger.exception("PaymentService encountered an error.")


    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.info("RabbitMQ connection closed.")

if __name__=='__main__':
    main()


