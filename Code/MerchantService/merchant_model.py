from pydantic import BaseModel



class MerchantRequest(BaseModel):
    name: str
    ssn: str
    email: str
    phoneNumber: str
    allowsDiscount: bool


