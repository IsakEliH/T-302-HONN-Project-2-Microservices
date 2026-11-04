from pydantic import BaseModel

class CreateBuyerRequest(BaseModel):
    name: str
    ssn: str
    email: str
    phoneNumber: str