import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
import uvicorn

from buyers import router as buyers_router
from orders import router as orders_router
from merchants import router as merchants_router
from products import router as product_router

app = FastAPI(title="API Layer")

app.include_router(orders_router)
app.include_router(buyers_router)
app.include_router(merchants_router)
app.include_router(product_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
