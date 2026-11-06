from fastapi import APIRouter, FastAPI, Response
from models.buyer import BuyerRequest
import httpx

app = FastAPI()
router = APIRouter(prefix="/api/buyers")
BUYER_URL = "http://buyer_service:8002/buyers"


@router.post("/")
async def post_buyer(buyerRequest: BuyerRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BUYER_URL}/", json=buyerRequest.model_dump())

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type="application/json"
    )


@router.get("/{buyerId}")
async def get_buyer(buyerId: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BUYER_URL}/{buyerId}")

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type="application/json"
    )


app.include_router(router)