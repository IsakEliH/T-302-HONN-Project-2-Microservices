import uvicorn
from fastapi import FastAPI

from buyer_endpoint import router as buyer_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(buyer_router)
    return app

app = create_app()

if __name__=='__main__':
    uvicorn.run('main:app')