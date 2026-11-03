from models.payment_models import Payment
from repository.peyment_repository import PaymentRepository
from models.payment_models import Payment
from paymentApi.payment_event_publisher import paymentSender


import pika
from retry import retry
import json


"""
Needs to
    - Take in the event sent from orderService
    - Collect the orderId and Card information
    - Validate Card information
    - Create a Payment object (orderId, paymentResult)
    - Save the object in the database
    - Send out an Event of the payment confirmation
"""

__QUEUE = "order"
__HOST = "rabbitmq"
__PORT = 5672


def __validateCardNumber(cardNumber: str):
    sum = 0
    length = len(cardNumber)

    for i in range(length):
        digit = int(cardNumber[i])
        offset_from_end = length - i

        if offset_from_end % 2 == 1:
            sum += digit
        elif digit < 5:
            sum += 2 * digit
        else:
            sum += 2 * digit - 9

    return sum % 10 == 0

def __ValidateExpirationMonth(expirationMonth):
    return 1<= expirationMonth <=12

def __validateExpirationYear(expirationYear):
    return len(str(expirationYear)) == 4

def __validateCvc(cvc):
    len(str(cvc)) == 3

def __validateCard(cardInfo):
    cardNumber: str = cardInfo.get("cardNumber")
    expirationMonth: int = cardInfo.get("expirationMonth")
    expirationYear: int = cardInfo.get("expirationYear")
    cvc: int = cardInfo.get("cvc")

    return __validateCardNumber(cardNumber) & __ValidateExpirationMonth(expirationMonth) & __validateExpirationYear(expirationYear) & __validateCvc(cvc) 

    
# Connects to the channel that the OrderService sends the order to
@retry(pika.exceptions.AMQPConnectionError, tries=3, delay=5, jitter=(1, 3))
def get_connection():
    parameters = pika.ConnectionParameters(
        host=__HOST,
        port=__PORT,
    )

    connection = pika.BlockingConnection(parameters)
    return connection


def consume():
    # Collects the orderId and cardInfo from the order sent
    def callback(ch, method, properties, body: bytes):
        event = json.loads(body.decode("utf-8"))
        orderId = event["orderId"]
        cardInfo = event.get("creditCard", {})

        paymentResult = __validateCard(cardInfo)
        paymentObj = Payment(orderId, paymentResult)
        post_payment(paymentObj)

        

    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue=__QUEUE, durable=True, arguments={"x-queue-type": "quorum"})
    channel.basic_consume(queue='messages', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


consume()

async def post_payment(payment: Payment):
    payment_repo = PaymentRepository()
    orderId = payment_repo.save_payment(payment)

    payment_sender = paymentSender()
    payment_sender.send_payment_event(payment)



    
    