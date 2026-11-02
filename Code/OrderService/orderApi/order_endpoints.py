from fastapi import APIRouter, FastAPI, HTTPException, status

from models import order_model
from models.order_model import OrderRequest
from rabbitmq.order_event_publisher import OrderSender
from repositories.order_repository import OrderRepository

app = FastAPI(title="OrderService")
router = APIRouter(prefix="/orders")


@router.post("/", tags=["orders"], status_code=status.HTTP_201_CREATED)
async def post_orders(request: OrderRequest):

    # TODO: If there is no merchant with the specific id,
    # return 400 with message "Merchant does not exit"
    # if request.merchantId is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="Merchant does not exit"
    #     )
    # if request.buyerId is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="Buyer does not exit"
    #     )
    # if request.productId is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="Product does not exit"
    #     )
    # TODO: If product with ProductId is sold out,
    # return 400 with message "Product is sold out"

    # TODO: If productId does not belong to merchantId,
    # return 400 with message "Product does not belong to merchant"

    # TODO: If merchant with merchantId does not allow discount, and discount is not None,
    # return 400 with message "Merchant does not allow discount"

    # Validation passed, create order and return orderId

    # reserve the product and store in database
    order_repo = OrderRepository()
    order_repo.save_order(request)

    # Send event that order has been created
    event_sender = OrderSender()
    event_sender.send_order_event(request)

    # return 201 status code with response of orderId
    return order_repo.latest_id


@router.get("/{id}", tags=["orders"], status_code=status.HTTP_200_OK)
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
