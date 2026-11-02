from fastapi import FastAPI, HTTPException, status
from schemas import Merchant, CreateMerchantRequest
from repository.merchant_repository import Mer


app = FastAPI(title="MerchantService")

@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def post_merchant(request: CreateMerchantRequest):
    ...



    #TODO Should return 201 HTTP Status Code with merchant the merchant id as the response message.


async def get_merchant(id: int) -> Merchant:
    ...


    #TODO Merchantservice should return 404 HTTP Status Code if the merchant with the corresponding id does not exist

    # Else it return the merchant 
