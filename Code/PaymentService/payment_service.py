from card_validation import validateCard
from models import CreditCard, OrderRequest, PaymentResult
from messaging import open_chanel, publish_payment, QUEUE
from payment_repository import PaymentRepository

import json



def save_payment(orderId: int, status: str):
    repository = PaymentRepository()
    repository.save_payment(orderId, status)



def main():
    """
    Opens up a channel and for loops through the QUEUE, so if a new event is sent it is processed
    - Checks the validation of the card info
    - Saves the order and the status of the validation
    - Creates a PaymentResult object to be sent as an event
    - Sends the event
    """
    channel = open_chanel()

    channel.queue_declare(
        queue=QUEUE,
        durable=True,
        arguments={"x-queue-type": "quorum"},
    )


    for method, _properties, body in channel.consume(QUEUE):
        event = json.loads(body.decode("utf-8"))
        orderId = event["orderId"]
        order = event["order"]

        if validateCard(order.get("creditCard")):
            status = "success"
        else:
            status = "failed"

        save_payment(orderId, status)

        result = PaymentResult(
            orderId=orderId,
            paymentResult=status
            )
        
        # )
        #     buyerEmail="EFTIR AÐ KLÁRA",
        #     merchantEmail="EFTIR AÐ KLÁRA"  #TODO fá email hjá bæði buyer og merchant eða taka út


        publish_payment(channel, "payments", result)

        channel.basic_ack(method.delivery_tag)


if __name__=='__main__':
    main()


