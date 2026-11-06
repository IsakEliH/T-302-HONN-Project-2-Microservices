from pydantic import BaseModel

class BuyerRequest(BaseModel):
    name: str
    ssn: str
    email: str
    phoneNumber: str