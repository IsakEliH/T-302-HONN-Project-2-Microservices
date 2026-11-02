from fastapi import APIRouter, FastAPI, HTTPException, status

from models.merchant_model import CreateMerchantRequest
from repository.merchant_repository import MerchantRepository


app = FastAPI(title="MerchantService")
router = APIRouter(prefix="/merchants")

@router.post("/", tags=["merchants"], status_code=status.HTTP_201_CREATED)
async def post_merchant(merchantRequest: CreateMerchantRequest):
    merchant_repo = MerchantRepository()
    merchantId = merchant_repo.save_merchant(merchantRequest)

    return merchantId

    

@router.post("/", tags=["merchants"], status_code=status.HTTP_201_CREATED)
async def get_merchant(merchantId: int) -> Merchant:
    merchant_repo = MerchantRepository()
    merchant : dict = merchant_repo.get_merchant(merchantId)

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant does not exist")

    
    return merchant


app.include_router(router)