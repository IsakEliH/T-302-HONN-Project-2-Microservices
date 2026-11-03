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

class PaymentResult(BaseModel):
    """paymentResult: success | failed"""
    orderID: int
    paymentResult: str

def build_inventory(inventory_request: InventoryRequest | dict) -> Inventory:
    return Inventory(
        merchantId=inventory_request.merchantId,
        productName=inventory_request.productName,
        price=inventory_request.price,
        quantity=inventory_request.quantity,
        reserved=0,
    ) if isinstance(inventory_request, InventoryRequest) else Inventory(
        merchantId=inventory_request["merchantId"],
        productName=inventory_request["productName"],
        price=inventory_request["price"],
        quantity=inventory_request["quantity"],
        reserved=0,
    )