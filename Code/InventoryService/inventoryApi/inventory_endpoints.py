from fastapi import APIRouter, FastAPI, status

from models.inventory_model import InventoryRequest

app = FastAPI(title="InventoryService")
router = APIRouter(prefix="/products")

#TODO: Somehow give OrderService ability to reserve a product item

@router.post("/", tags=["products"], status_code=status.HTTP_201_CREATED)
async def post_orders(request: InventoryRequest):
    #TODO: Store in db
    #TODO: Return product id
    pass


@router.get("/{productId}", tags=["products"], status_code=status.HTTP_200_OK)
async def get_orders(productId: int):

    #TODO: raise 404 error if not exist: "Product does not exist"
    #TODO: Return respond body for the productId
    pass


app.include_router(router)
