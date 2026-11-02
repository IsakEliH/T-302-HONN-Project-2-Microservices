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
    discount: float | None = None


def build_order(order_dict: dict) -> Order:
    productId: int = order_dict.get("productId")
    merchantId: int = order_dict.get("merchantId")
    buyerId: int = order_dict.get("buyerId")
    cardNumber: str = order_dict.get("cardNumber")
    totalPrice: float = order_dict.get("totalPrice")

    return Order(
        productId=productId,
        merchantId=merchantId,
        buyerId=buyerId,
        cardNumber=cardNumber,
        totalPrice=totalPrice,
    )
