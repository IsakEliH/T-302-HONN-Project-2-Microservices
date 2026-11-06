from fastapi import APIRouter, Response
from OrderService.models.order_model import Order
import httpx

router = APIRouter(prefix="/api/orders")

ORDER_URL = "http://order-service:8000/orders"


@router.post("/")
async def post_order(orderRequest: Order):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ORDER_URL}/", json=orderRequest)

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type="application/json"
    )


@router.get("/{orderId}")
async def get_order(orderId: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORDER_URL}/{orderId}")

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type="application/json"
    )