from fastapi import APIRouter, FastAPI, HTTPException, status

from models.buyer_model import CreateBuyerRequest
from repository.buyer_repository import BuyerRepository

app = FastAPI(title="BuyerService")
router = APIRouter(prefix="/buyers")

@router.post("/", tags=["buyers"], status_code=status.HTTP_201_CREATED)
async def post_buyer(buyerRequest: CreateBuyerRequest):
    buyer_repo = BuyerRepository()
    buyerId = buyer_repo.save_buyer(buyerRequest)

    return buyerId


@router.get("/", tags=["buyers"], status_code=status.HTTP_201_CREATED)
async def get_buyer(buyerId: int):
    buyer_repo = BuyerRepository()
    buyer : dict = buyer_repo.get_buyer(buyerId)

    if not buyer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer does not exist")

    return buyer

app.include_router(router)