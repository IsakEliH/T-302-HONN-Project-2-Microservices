from fastapi import FastAPI, HTTPException, status
from Code.MerchantService.models.schemas import Merchant, CreateMerchantRequest
from repository.merchant_repository import MerchantRepository


app = FastAPI(title="MerchantService")

@app.post("/merchants", status_code=status.HTTP_201_CREATED)
async def post_merchant(merchantRequest: CreateMerchantRequest):
    merchant_repo = MerchantRepository()
    merchantId = merchant_repo.save_merchant(merchantRequest)

    return merchantId

    

@app.post("/merchants{id}", status_code=status.HTTP_201_CREATED)
async def get_merchant(merchantId: int) -> Merchant:
    merchant_repo = MerchantRepository()
    merchant : dict = merchant_repo.get_merchant(merchantId)

    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant does not exist")

    
    return merchant
