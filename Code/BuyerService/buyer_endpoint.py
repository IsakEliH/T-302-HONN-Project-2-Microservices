from fastapi import APIRouter, FastAPI, HTTPException, status

from buyer_model import BuyerRequest
from buyer_repository import BuyerRepository

app = FastAPI(title="BuyerService")
router = APIRouter(prefix="/buyers")

@router.post("/", tags=["buyers"], status_code=status.HTTP_201_CREATED)
async def post_buyer(buyerRequest: BuyerRequest):
    """
    Takes in buyer object
    Saves the buyer in the buyer database
    Returns the buyers Id
    """
    buyer_repo = BuyerRepository()
    buyerId = buyer_repo.save_buyer(buyerRequest)

    return buyerId



@router.get("/{buyerId}", tags=["buyers"], status_code=status.HTTP_201_CREATED)
async def get_buyer(buyerId: int):
    """
    Takes in buyers Id
    Retrieves the buyers object from Id in the buyers database
    Returns the buyer object
    """
    buyer_repo = BuyerRepository()
    buyer : dict = buyer_repo.get_buyer(buyerId)

    if not buyer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer does not exist")

    return buyer

app.include_router(router)