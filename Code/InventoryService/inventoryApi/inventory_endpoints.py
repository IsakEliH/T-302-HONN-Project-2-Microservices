from fastapi import APIRouter, FastAPI, HTTPException, status

from models.inventory_model import InventoryRequest, build_inventory
from repositories.inventory_repository import InventoryRepository

TAG: str = "products"

app = FastAPI(title="InventoryService")
router = APIRouter(prefix="/" + TAG, tags=[TAG])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_product(request: InventoryRequest):
    # Store in db (with reserved=0)
    inventory_repo = InventoryRepository()
    inventory = build_inventory(request)
    inventory_repo.save_product(inventory)

    # Return product id with status code 201
    product_id = inventory_repo.latest_id
    return product_id


@router.get("/{productId}", status_code=status.HTTP_200_OK)
async def get_product(productId: int):
    # get product from db
    inventory_repo = InventoryRepository()
    product = inventory_repo.get_product(productId)

    # raise 404 error if not exist: "Product does not exist"
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist"
        )

    # Return respond body Inventory for the productId
    return build_inventory(product)

# TODO: Add endpoint to reserve a product item (for OrderService)

app.include_router(router)
