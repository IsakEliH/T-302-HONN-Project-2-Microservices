import logging
from typing import Optional, Dict
import resend

from config import config
from models.event_models import OrderCreatedEvent, PaymentEvent

logger = logging.getLogger("EmailService")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class EmailSender:
    def __init__(self, api_key: Optional[str] = None, sender_email: Optional[str] = None):
        self.api_key = api_key or config.RESEND_API_KEY
        self.sender_email = sender_email or config.RESEND_SENDER_EMAIL
        resend.api_key = self.api_key

    def send_email(self, to: str, subject: str, text: str, html: Optional[str] = None) -> bool:
        """
        Sends an email using the Resend API.
        """
        if not to or not to.strip():
            logger.warning("Recipient email is empty; skipping sending.")
            return False

        params: resend.Emails.SendParams = {
            "from": self.sender_email,
            "to": [to.strip()],
            "subject": subject,
            "text": text,
        }
        if html:
            params["html"] = html
        else:
            params["html"] = f"<p>{text.replace(chr(10), '<br/>')}</p>"

        try:
            response = resend.Emails.send(params)
            logger.info("Successfully sent email to %s (Subject: '%s'). Response: %s", to, subject, response)
            return True
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to, exc)
            return False

    def handle_order_created(self, event: OrderCreatedEvent) -> Dict[str, bool]:
        """
        Processes Order-Created event and sends notification emails to buyer and merchant.
        Subject: 'Order has been created'
        Body includes: order ID, product name, total price (with discount included).
        """
        subject = "Order has been created"
        body = (
            f"Order {event.order_id} has been created.\n"
            f"Product: {event.product_name or 'N/A'}\n"
            f"Total Price: {event.total_price}"
        )
        html = (
            f"<h3>Order Created Confirmation</h3>"
            f"<p>Order <strong>#{event.order_id}</strong> has been created.</p>"
            f"<ul>"
            f"<li><strong>Product:</strong> {event.product_name or 'N/A'}</li>"
            f"<li><strong>Total Price:</strong> {event.total_price}</li>"
            f"<li><strong>Discount:</strong> {event.discount}</li>"
            f"</ul>"
        )

        results = {}
        if event.buyer_email:
            results["buyer"] = self.send_email(event.buyer_email, subject, body, html)
        else:
            logger.warning("No buyer email provided in OrderCreated event for order %s", event.order_id)

        if event.merchant_email:
            results["merchant"] = self.send_email(event.merchant_email, subject, body, html)
        else:
            logger.warning("No merchant email provided in OrderCreated event for order %s", event.order_id)

        return results

    def handle_payment_success(self, event: PaymentEvent) -> Dict[str, bool]:
        """
        Processes Payment-Success event and sends notification emails.
        Subject: 'Order has been purchased'
        Body: 'Order {order_id} has been successfully purchased'
        """
        subject = "Order has been purchased"
        body = f"Order {event.order_id} has been successfully purchased"
        html = f"<p>Order <strong>#{event.order_id}</strong> has been successfully purchased.</p>"

        results = {}
        if event.buyer_email:
            results["buyer"] = self.send_email(event.buyer_email, subject, body, html)
        if event.merchant_email:
            results["merchant"] = self.send_email(event.merchant_email, subject, body, html)

        return results

    def handle_payment_failure(self, event: PaymentEvent) -> Dict[str, bool]:
        """
        Processes Payment-Failure event and sends notification emails.
        Subject: 'Order purchase failed'
        Body: 'Order {order_id} purchase has failed'
        """
        subject = "Order purchase failed"
        body = f"Order {event.order_id} purchase has failed"
        html = f"<p>Order <strong>#{event.order_id}</strong> purchase has failed.</p>"

        results = {}
        if event.buyer_email:
            results["buyer"] = self.send_email(event.buyer_email, subject, body, html)
        if event.merchant_email:
            results["merchant"] = self.send_email(event.merchant_email, subject, body, html)

        return results
