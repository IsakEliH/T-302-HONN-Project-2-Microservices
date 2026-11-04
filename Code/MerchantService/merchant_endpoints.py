from fastapi import APIRouter, FastAPI, HTTPException, status

from merchant_model import MerchantRequest
from merchant_repository import MerchantRepository


app = FastAPI(title="MerchantService")
router = APIRouter(prefix="/merchants")

@router.post("/", tags=["merchants"], status_code=status.HTTP_201_CREATED)
async def post_merchant(merchantRequest: MerchantRequest):
    """
    Takes in a merchant object
    Saves it to the merchant database
    Returns the merchant Id
    """
    merchant_repo = MerchantRepository()
    merchantId = merchant_repo.save_merchant(merchantRequest)

    return merchantId

    

@router.get("/{merchantId}", tags=["merchants"], status_code=status.HTTP_200_OK)
async def get_merchant(merchantId: int):
    """
    Takes in int merchant Id
    Retrieves the merchant object form id
    Returns the merchant object
    """
    merchant_repo = MerchantRepository()
    merchant : dict = merchant_repo.get_merchant(merchantId)

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant does not exist")

    
    return merchant


app.include_router(router)