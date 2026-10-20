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


def build_order(order: dict) -> Order:
    pass
