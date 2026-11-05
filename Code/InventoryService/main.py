import threading

import uvicorn
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from inventoryApi.inventory_endpoints import router as order_router
from rabbitmq.inventory_consumer import InventoryConsumer


# Allows both the FastAPI server and the RabbitMQ consumer to run concurrently
@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = InventoryConsumer()

    thread = threading.Thread(target=consumer.start_consuming, daemon=True)
    thread.start()

    yield

    consumer.stop_consuming()
    thread.join(timeout=5)


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(order_router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8003, reload=True)
