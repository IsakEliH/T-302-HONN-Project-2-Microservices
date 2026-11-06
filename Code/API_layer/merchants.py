from fastapi import APIRouter, Response
from MerchantService.merchant_model import MerchantRequest
import httpx

router = APIRouter(prefix="/api/merchants")

MERCHANT_URL = "http://merchant-service:8000/merchants"


@router.post("/")
async def post_merchant(merchantRequest: MerchantRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MERCHANT_URL}/", json=merchantRequest)

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type="application/json"
    )


@router.get("/{merchantId}")
async def get_merchant(merchantId: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MERCHANT_URL}/{merchantId}")

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type="application/json"
    )