import requests
from fastapi import APIRouter, FastAPI, HTTPException, status

from models import order_model
from models.order_model import MERCHANT_URL, OrderRequest
from rabbitmq.order_event_publisher import OrderSender
from repositories.order_repository import OrderRepository

app = FastAPI(title="OrderService")
router = APIRouter(prefix="/orders")


@router.post("/", tags=["orders"], status_code=status.HTTP_201_CREATED)
async def post_orders(request: OrderRequest):

    # Keep responses as raw Response objects first
    merchant_response = requests.get(
        f"{MERCHANT_URL}/merchants/{request.merchantId}"
    )
    buyer_response = requests.get(
        f"{order_model.BUYER_URL}/buyers/{request.buyerId}"
    )
    inventory_response = requests.get(
        f"{order_model.INVENTORY_URL}/products/{request.productId}"
    )

    # Validations for 404 Not Found
    if merchant_response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Merchant does not exist"
        )
    if buyer_response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Buyer does not exist"
        )
    if inventory_response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product does not exist"
        )

    # Now extract the JSON dictionaries safely
    merchant_data = merchant_response.json()
    inventory_data = inventory_response.json()

    # If product with ProductId is sold out,
    # return 400 with message "Product is sold out"
    if inventory_data.get("quantity") == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product is sold out"
        )

    # If productId does not belong to merchantId,
    # return 400 with message "Product does not belong to merchant"
    if inventory_data.get("merchantId") != request.merchantId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product does not belong to merchant",
        )

    # If merchant with merchantId does not allow discount, and discount is not None,
    # return 400 with message "Merchant does not allow discount"
    if merchant_data.get("allowDiscount") is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Merchant does not allow discount",
        )

    # Validation passed, create order and return orderId

    # reserve the product
    order_model.reserve_product(request.productId)
    
    # store in database
    order_repo = OrderRepository()
    order_repo.save_order(request)

    order_id = order_repo.latest_id

    # Send event that order has been created
    event_sender = OrderSender()
    event_sender.send_order_event(request, order_id)

    # return 201 status code with response of orderId
    return order_id


@router.get("/{orderId}", tags=["orders"], status_code=status.HTTP_200_OK)
async def get_orders(orderId: int):
    # Get order from orderId
    order_repo = OrderRepository()
    order_dict: dict = order_repo.get_order(orderId)

    # If order with id does not exist,
    # return 404 with message "Order does not exist"
    if not order_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist"
        )

    # We need to create Order which masks and does not show all data
    order = order_model.build_order(order_dict)
    # return 200 status code with response of order
    return order


app.include_router(router)