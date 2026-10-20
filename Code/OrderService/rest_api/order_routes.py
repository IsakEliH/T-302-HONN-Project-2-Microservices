from fastapi import FastAPI, HTTPException, status
from schemas import CreateOrderRequest, Order

app = FastAPI(title="OrderService (REST)")


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def post_orders(request: CreateOrderRequest) -> Order:

    # TODO: If there is no merchant with the specific id,
    # return 400 with message "Merchant does not exit"
    if request.merchantId is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Merchant does not exit"
        )
    if request.buyerId is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Buyer does not exit"
        )
    if request.productId is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product does not exit"
        )
    # TODO: If product with ProductId is sold out,
    # return 400 with message "Product is sold out"

    # TODO: If productId does not belong to merchantId,
    # return 400 with message "Product does not belong to merchant"

    # TODO: If merchant with merchantId does not allow discount, and discount is not None,
    # return 400 with message "Merchant does not allow discount"

    # Validation passed, create order and return orderId

    # TODO: reserve the product and store in database
    # TODO: Send event that order has been created
    # TODO return 201 status code with response of orderId


@app.get("/orders/{id}", status_code=status.HTTP_200_OK)
async def get_orders(id: int) -> Order:
    # TODO: If order with id does not exist,
    # return 404 with message "Order does not exist"

    # TODO: When return the order, make sure to mask the card number,
    # e.g. "************1234"
    # TODO: total price should be calculated as:
    # product price (of product with productId) - discount (if any)
    # -> price * (1-discount) if discount is not None else price
    # TODO: return 200 status code with response of order

    pass
