from fastapi import APIRouter, Response
from InventoryService.models.inventory_model import Inventory
import httpx

router = APIRouter(prefix="/api/products")

PRODUCT_URL = "http://products-service:8000/products"


@router.post("/")
async def post_product(productrequest: Inventory):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PRODUCT_URL}/", json=productrequest)

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type="application/json"
    )


@router.get("/{itemId}")
async def get_product(itemId: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCT_URL}/{itemId}")

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type="application/json"
    )