import uvicorn
from fastapi import FastAPI

from MerchantService.merchant_endpoints import router as merchant_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(merchant_router)
    return app


app = create_app()

if __name__=='__main__':
    uvicorn.run('main:app', host='localhost', port=8001, reload=True)