from pydantic import BaseModel


class InventoryRequest(BaseModel):
    merchantId: int
    productName: str
    price: int
    quantity: int


class Inventory(BaseModel):
    merchantId: int
    productName: str
    price: int
    quantity: int
    reserved: int
