from pydantic import BaseModel


class Merchant(BaseModel):
    name: str
    snn: str
    email: str
    phoneNumber: str
    allowsDiscount: bool




def build_merchant(merchant: dict) -> Merchant:
    pass