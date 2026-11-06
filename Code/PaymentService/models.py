from pydantic import BaseModel

class PaymentResult(BaseModel):
    orderId: int
    paymentResult: str
    buyerEmail: str | None = None
    merchantEmail: str | None = None

class PaymentResultInventory(BaseModel):
    productId: int
    paymentResult: str


class CreditCard(BaseModel):
    cardNumber: str
    expirationMonth: int
    expirationYear: int
    cvc: int


class OrderRequest(BaseModel):
    productId: int
    merchantId: int
    buyerId: int
    creditCard: CreditCard
    discount: float = 0.0