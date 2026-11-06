import uvicorn
from fastapi import FastAPI

# Change this from 'from MerchantService.merchant_endpoints...' to:
from merchant_endpoints import router as merchant_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(merchant_router)
    return app


app = create_app()

if __name__ == '__main__':
    # Change host from 'localhost' to '0.0.0.0' for Docker compatibility
    uvicorn.run('main:app', host="0.0.0.0", port=8001)