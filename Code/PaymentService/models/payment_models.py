from pydantic import BaseModel
class Payment(BaseModel):
    orderId: str
    paymentResult: bool