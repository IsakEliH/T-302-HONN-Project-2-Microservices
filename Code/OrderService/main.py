import uvicorn
from fastapi import FastAPI

from orderApi.order_endpoints import router as order_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(order_router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8004)
