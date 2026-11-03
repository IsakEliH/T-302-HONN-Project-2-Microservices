import requests
from pydantic import BaseModel

MERCHANT_URL = "http://localhost:8001"
BUYER_URL = "http://localhost:8002"
INVENTORY_URL = "http://localhost:8003"

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


class OrderRequest(BaseModel):
    productId: int
    merchantId: int
    buyerId: int
    creditCard: CreditCard
    discount: float = 0.0


class OrderEmailRequest(BaseModel):
    orderId: int
    productId: int
    merchantId: int
    buyerId: int
    product_name: str
    buyer_email: str
    merchant_email: str
    total_price: float
    discount: float = 0.0


def build_order_email_request(
    request: OrderRequest, order_id: int
) -> OrderEmailRequest:

    discount = request.discount
    price = get_price(request.productId)
    totalPrice = calculate_total_price(price, discount)

    return OrderEmailRequest(
        orderId=order_id,
        productId=request.productId,
        merchantId=request.merchantId,
        buyerId=request.buyerId,
        product_name=get_product_name(request.productId),
        buyer_email=get_buyer_email(request.buyerId),
        merchant_email=get_merchant_email(request.merchantId),
        total_price=totalPrice,
        discount=discount,
    )


def build_order(order_dict: dict) -> Order:
    """
    Build the order we want in the GET endpoint

    :param order_dict: the order structure of POST
    :type order_dict: dict
    :return: return the BaseModel Order class for our GET endpoint
    :rtype: Order
    """

    product_id: int = order_dict.get("productId", int)
    merchant_id: int = order_dict.get("merchantId", int)
    buyer_id: int = order_dict.get("buyerId", int)

    # Mask card number
    card_number: str = order_dict.get("creditCard", {}).get("cardNumber", str)
    new_card_number = 12 * "*" + card_number[12::]

    # Calculate total price
    discount: float = order_dict.get("discount", float)

    price = get_price(product_id)
    totalPrice = calculate_total_price(price, discount)

    return Order(
        productId=product_id,
        merchantId=merchant_id,
        buyerId=buyer_id,
        cardNumber=new_card_number,
        totalPrice=totalPrice,
    )


def calculate_total_price(price: float, discount: float) -> float:
    if discount is not None:
        return price * (1 - discount)
    else:
        return price



def get_merchant_email(merchant_id: int) -> str:
    response = requests.get(f"{MERCHANT_URL}/merchants/{merchant_id}").json()
    email = response.get("email", str)
    return email

def get_buyer_email(buyer_id: int) -> str:
    response = requests.get(f"{BUYER_URL}/buyers/{buyer_id}").json()
    email = response.get("email", str)
    return email

def get_product_name(product_id: int) -> str:
    response = requests.get(f"{INVENTORY_URL}/products/{product_id}").json()
    name = response.get("name", str)
    return name

def get_price(product_id: int) -> float:
    response = requests.get(f"{INVENTORY_URL}/products/{product_id}").json()
    price = response.get("price", float)
    return price