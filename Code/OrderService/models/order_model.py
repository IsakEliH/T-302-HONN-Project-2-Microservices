import requests
from pydantic import BaseModel


class Order(BaseModel):
    productId: int
    merchantId: int
    buyerId: int
    cardNumber: str  # "************1234"
    totalPrice: float


class CreditCard(BaseModel):
    cardNumber: str
    expirationMonth: int
    expirationYear: int
    cvc: int


class CreateOrderRequest(BaseModel):
    productId: int
    merchantId: int
    buyerId: int
    creditCard: CreditCard
    discount: float = 0.0


def build_order(order_dict: dict) -> Order:
    """
    Build the order we want in the GET endpoint

    :param order_dict: the order structure of POST
    :type order_dict: dict
    :return: return the BaseModel Order class for our GET endpoint
    :rtype: Order
    """
    BASE_URL = "http://localhost:8000"

    product_id: int = order_dict.get("productId", int)
    merchant_id: int = order_dict.get("merchantId", int)
    buyer_id: int = order_dict.get("buyerId", int)
    card_number: str = order_dict.get("creditCard", {}).get("cardNumber", str)

    discount: float = order_dict.get("discount", float)

    # Calculate total price
    # Need to get price first
    # response = requests.get(f"{BASE_URL}/items/{merchantId}").json()
    # price = response.get("price", int)
    # totalPrice: float = price * (1 - discount)

    # TODO: FIX the get request this is temporary
    totalPrice = discount

    return Order(
        productId=product_id,
        merchantId=merchant_id,
        buyerId=buyer_id,
        cardNumber=card_number,
        totalPrice=totalPrice,
    )
