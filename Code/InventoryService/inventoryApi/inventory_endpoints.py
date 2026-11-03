from fastapi import APIRouter, FastAPI, status

from InventoryService.models.inventory_model import InventoryRequest

app = FastAPI(title="InventoryService")
router = APIRouter(prefix="/products")


@router.post("/", tags=["products"], status_code=status.HTTP_201_CREATED)
async def post_orders(request: InventoryRequest):

    pass


@router.get("/{productId}", tags=["products"], status_code=status.HTTP_200_OK)
async def get_orders(productId: int):
    pass


app.include_router(router)
