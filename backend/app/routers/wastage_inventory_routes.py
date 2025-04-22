#  backend/app/routers/wastage_inventory_routes.py
from backend.app.database.redisclient import get_redis_dependency
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
import logging
import requests
from fastapi import Response
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.database import get_async_db
from datetime import datetime
from backend.app.schema.wastage_inventory_schema import (
    WastageInventoryCreate,
    WastageInventoryOut,
    WastageInventoryUpdate,
    WastageInventoryRedisIn,
    WastageInventoryRedisOut,
    WastageInventorySearch,
    RedisSearchResult
)
from typing import Optional, Union, Dict, Any
from pydantic import ValidationError
from backend.app.models.wastege_inventory_model import WastageInventory
from backend.app.curd.wastage_inventory_curd import WastageInventoryService
from backend.app.interface.wastage_inventory_interface import WastageInventoryInterface
from backend.app.schema.inventory_ComboBox_schema import InventoryComboBoxResponse

# Dependency to get the Wastage inventory service
def get_Wastage_inventory_service(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> WastageInventoryService:
    return WastageInventoryService(redis)

# Set up the router
router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --------------------------
# Asynchronous Endpoints
# --------------------------

# upload all wastage inventory entries from local Redis to the database after click on upload data button
@router.post(
    "/upload-wastage-inventory/",
    response_model=List[WastageInventoryRedisOut],
    status_code=200,
    summary="Upload all wastage inventory entries from Redis to database",
    description="Uploads all wastage inventory entries from local Redis to the database",
    tags=["Upload Inventory (DataBase)"]
)
async def upload_wastage_inventory(
    db: AsyncSession = Depends(get_async_db),
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    """Upload all wastage inventory entries from Redis to the database.
    
    Returns:
        List of WastageInventoryRedisOut objects with upload status for each item
    """
    try:
        logger.info("Starting Redis to database upload process")
        
        # Get data from service
        uploaded_items = await service.upload_wastage_inventory(db)
        
        if not uploaded_items:
            logger.warning("No inventory items found in Redis for upload")
            raise HTTPException(
                status_code=404,
                detail="No inventory items found in Redis"
            )
            
        logger.info(f"Successfully processed {len(uploaded_items)} items")
        return uploaded_items
        
    except ValidationError as ve:
        logger.error(f"Data validation error: {ve}", exc_info=True)
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Data validation failed",
                "errors": ve.errors()
            }
        )
    except HTTPException:
        # Re-raise existing HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload inventory data: {str(e)}"
        )  

# Show all inventory entries directly from local Redis according in sequence alphabetical order after clicking `Show All` button
@router.get("/show-all-wastage-inventory/",
            response_model=List[WastageInventoryRedisOut],
            status_code=200,
            summary="Load wastage inventory entries from the database",
            description="This endpoint is used to get all entries from the database. It returns a list of entries.",
            response_model_exclude_unset=True,
            tags=["Show all Inventory (Redis)"]
)
async def show_wastage_inventory(
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    """Get all inventory items"""
    try:
        logger.info("Fetching all inventory data from Redis")
        items = await service.show_all_wastage_inventory_from_redis()
        
        if not items:
            logger.warning("No inventory data found in Redis cache")
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "not_found",
                    "message": "No inventory data available in cache"
                }
            )
            
        logger.info(f"Successfully retrieved {len(items)} cached entries")
        return items
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Data validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "message": "Invalid data format in Redis cache",
                "error": str(e)
            }
        )

# CREATE: Add a new WastageInventory to the inventory
@router.post("/create-wastage-inventory/",
    response_model=WastageInventoryRedisOut,
    status_code=200,
    summary="Create a new WastageInventory in the inventory",
    description="This endpoint is used to create a new WastageInventory in the inventory. It takes a JSON payload with the necessary fields and values, and returns the created WastageInventory.",
    response_model_exclude_unset=True,
    tags=["create Inventory (Redis)"]
)
async def create_wastage_inventory(
    item: WastageInventoryCreate,
    db: AsyncSession = Depends(get_async_db),
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    try:
        item_data = item.dict(exclude_unset=True)
        logger.info(f"New item created: {item_data}")
        return await service.create_wastage_inventory(db, item_data)
    except Exception as e:
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# READ: search/fetch an inventory which is match from [Inventory ID, Project ID, Product ID, Employee name]
@router.get("/search-wastage-inventory/",
            response_model=List[RedisSearchResult],
            status_code=200,
            summary="Search wastage inventory by multiple fields",
            description="Search inventory wastage by inventory_id, project_id, product_id, or employee_name",
            response_model_exclude_unset=True,
            tags=["search Inventory (Redis)"]
)
async def search_wastage_inventory(
    inventory_id: Optional[str] = None,
    product_id: Optional[str] = None,
    project_id: Optional[str] = None,
    employee_name: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    results = await service.search_wastage_by_fields(
        db,
        inventory_id=inventory_id,
        project_id=project_id,
        product_id=product_id,
        employee_name=employee_name
    )
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="No matching inventory wastage found"
        )
    
    return results

# READ ALL: List current added wastage inventory
@router.get("/list-added-wastage-inventory/",
            response_model=list[WastageInventoryRedisOut],
            status_code=200,
            summary="Load wastage inventory from the database",
            description="This endpoint is used to get all entries from the database. It returns a list of entries.",
            response_model_exclude_unset=True,
            tags=["load Inventory (Redis)"]
)
async def list_added_wastage_inventory(
    skip: int = 0,
    db: AsyncSession = Depends(get_async_db),
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    """Get all inventory items"""
    try:
        items = await service.list_added_wastage_inventory(db, skip)
        logger.info(f"Retrieved {len(items)} inventory items")
        return items
    except Exception as e:
        logger.error(f"Error fetching inventory items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#  update/edit existing WastageInventory by [InventoryID, EmployeeName]
@router.put(
    "/update-wastage-inventory/{employee_name}/{inventory_id}/",
    response_model=WastageInventoryRedisOut,
    status_code=200,
    summary="Update wastage inventory",
    description="Update inventory wastage by employee_name and inventory_id",
    response_model_exclude_unset=True,
    tags=["update Inventory (Redis)"]
)
async def update_wastage_inventory(
    employee_name: str,
    inventory_id: str,
    update_data: WastageInventoryUpdate,
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    """
    Update an inventory wastage by employee_name and inventory_id.
    Immutable fields (IDs, barcodes, timestamps) cannot be changed.
    """
    # Convert Pydantic model to dict and add path parameters
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict.update({
        'employee_name': employee_name,
        'inventory_id': inventory_id
    })
    
    return await service.update_wastage_inventory(update_dict)  

# DELETE: Delete an inventory WastageInventory
@router.delete(
    "/delete-wastage-inventory/{employee_name}/{inventory_id}/",
    status_code=200,
    response_model=WastageInventoryRedisOut,  # Or create a proper response model
    summary="Delete wastage inventory",
    description="Delete an inventory wastage by employee name and inventory ID",
    tags=["Delete Inventory (Redis)"]
)
async def delete_wastage_inventory(
    employee_name: str,
    inventory_id: str,
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    try:
        result = await service.delete_wastage_inventory(
            employee_name=employee_name,
            inventory_id=inventory_id
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting wastage inventory: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e))

# GET: Get inventory by inventory_id, and employee_name
@router.get("/get-wastage-inventory/{employee_name}/{inventory_id}/",
            response_model=WastageInventoryRedisOut,
            status_code=200,
            summary="Get wastage inventory by employee and inventory ID",
            description="Get inventory wastage by employee_name and inventory_id",
            response_model_exclude_unset=True,
            tags=["Get Inventory (Redis)"]
)
async def get_wastage_inventory_by_id(
    employee_name: str,
    inventory_id: str,
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    """Fetch inventory data from Redis by employee name and inventory ID"""
    try:
        return await service.get_wastage_inventory(employee_name, inventory_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory item: {e}") 
        raise HTTPException(status_code=500, detail=str(e))


#  Drop Down search list option  ComboBox Widget for inventory_name across multiple key patterns
@router.get("/inventory-combobox/",
            response_model=InventoryComboBoxResponse,
            status_code=200,
            summary="Search inventory items",
            description="Search inventory items across multiple Redis key patterns",
            tags=["Combobox Search"]
)
async def inventory_ComboBox(
    search_term: Optional[str] = None,
    skip: int = 0,
    service: WastageInventoryService = Depends(get_Wastage_inventory_service)
):
    """Search inventory items by name across multiple key patterns"""
    try:
        return await service.inventory_ComboBox(
            search_term=search_term,
            skip=skip
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching inventory items: {e}") 
        raise HTTPException(status_code=500, detail=str(e))