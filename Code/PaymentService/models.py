from pydantic import BaseModel

class PaymentResult(BaseModel):
    orderId: int
    paymentResult: str
    # buyerEmail: str
    # merchantEmail: str    TODO Taka út?? Halda????

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