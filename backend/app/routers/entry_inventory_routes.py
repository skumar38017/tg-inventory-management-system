# backend/app/routers/entry_inventory_routes.py
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from backend.app.database.database import get_async_db
from datetime import datetime
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryCreate,
    EntryInventoryUpdate,
    EntryInventoryOut,
    InventoryRedisOut,
    EntryInventorySearch,
    DateRangeFilter
)
from backend.app.curd.entry_inverntory_curd import EntryInventoryService
from backend.app.interface.entry_inverntory_interface import EntryInventoryInterface

# Dependency to get the entry inventory service
def get_entry_inventory_service() -> EntryInventoryService:
    return EntryInventoryService()

# Set up the router
router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --------------------------
# Asynchronous Endpoints
# --------------------------

#  Filter inventory from database by date range without passing any `IDs`
@router.get(
    "/date-range",
    response_model=List[EntryInventoryOut],
    status_code=200,
    summary="Filter inventory by date range",
    description="Get inventory items within a specific date range",
    response_model_exclude_unset=True,
)
async def get_inventory_by_date_range(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """Get inventory items within a date range"""
    try:
        # FastAPI automatically converts query params to date objects
        if from_date > to_date:
            raise HTTPException(
                status_code=400,
                detail="From date cannot be after To date"
            )
            
        results = await service.get_by_date_range(db, DateRangeFilter(
            from_date=from_date,
            to_date=to_date
        ))
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No items found between {from_date} and {to_date}"
            )
            
        return results
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Date range filter failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)  # Return the actual error message
        )

# Refrech record in UI and show all updated data directly after clicking {sync} button [/sync/]
@router.post("/sync/",
    status_code=200,
    summary="Sync database with Redis",
    description="Stores all inventory entries in Redis cache",
    responses={
        200: {"description": "Successfully synced with Redis"},
        500: {"description": "Internal server error during sync"}
    }
)
async def sync_redis(
    service: EntryInventoryService = Depends(get_entry_inventory_service),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Synchronize all inventory data from database to Redis cache.
    
    This endpoint will:
    1. Fetch all inventory entries from the database
    2. Store them in Redis with proper serialization
    3. Return success/failure status
    """
    try:
        logger.info("Starting Redis sync operation")
        success = await service.store_inventory_in_redis(db)
        
        if not success:
            logger.warning("Redis sync completed with warnings")
            return {"status": "completed with warnings"}
            
        logger.info("Redis sync completed successfully")
        return {"status": "success", "message": "All inventory entries synced to Redis"}
        
    except HTTPException:
        # Re-raise HTTPExceptions (they're intentional)
        raise
    except Exception as e:
        logger.error(f"Critical error during Redis sync: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "message": "Failed to sync with Redis",
                "error": str(e)
            }
        )

# Show all inventory entries directly from local Redis Database  (no search) according in sequence alphabetical order after clicking `Show All` button
@router.get("/show-all/",
    response_model=List[InventoryRedisOut],
    status_code=200,
    summary="Show all Redis-cached inventory",
    description="Retrieves all inventory entries from Redis cache",
    responses={
        200: {"description": "Successfully retrieved cached data"},
        404: {"description": "No cached data found"},
        500: {"description": "Internal server error during retrieval"}
    }
)
async def show_all_redis(
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """
    Retrieve all inventory data from Redis cache.
    
    This endpoint will:
    1. Fetch all cached inventory entries from Redis
    2. Validate and deserialize the data
    3. Return the sorted list of inventory items
    """
    try:
        logger.info("Fetching all inventory data from Redis")
        cached_data = await service.show_all_inventory_from_redis()
        
        if not cached_data:
            logger.warning("No inventory data found in Redis cache")
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "not_found",
                    "message": "No inventory data available in cache"
                }
            )
            
        logger.info(f"Successfully retrieved {len(cached_data)} cached entries")
        return cached_data
        
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
    except Exception as e:
        logger.error(f"Failed to retrieve cached data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "message": "Failed to retrieve cached data",
                "error": str(e)
            }
        )

# CREATE: Add a new entry to the inventory
@router.post("/create-item/",
    response_model=EntryInventoryOut,
    status_code=200,
    summary="Create a new entry in the inventory",
    description="This endpoint is used to create a new entry in the inventory. It takes a JSON payload with the necessary fields and values, and returns the created entry.",
    response_model_exclude_unset=True,
)
async def create_inventory_item_route(
    item: EntryInventoryCreate,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    try:
        # Convert to dict and process
        item_data = item.dict(exclude_unset=True)
        logger.info(f"New item created: {item_data}")

        if not item_data:
            logger.error("Failed to create inventory item: item is None.")
            raise HTTPException(status_code=400, detail="Failed to create inventory item")
        
        return await service.create_entry_inventory(db, item_data)
    except Exception as e:
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=400, detail=str(e))
# ________________________________________________________________________________________

# READ: Get an inventory which is match from inventry ID
@router.get("/fetch/{inventory_id}",
            response_model=EntryInventoryOut,
            status_code=200,
            summary="Get an entry from the inventory by its inventory_id",
            description="This endpoint is used to get an entry from the inventory by its inventory_id. It takes a inventory_id as a parameter and returns the entry with the specified inventory_id.",
            response_model_exclude_unset=True,
)
async def get_inventory_item(
    inventory_id: str, 
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    entry_inventory = await service.get_by_inventory_id(db, inventory_id)
    if not entry_inventory:
        raise HTTPException(status_code=404, detail="EntryInventory not found")
    return entry_inventory

# READ ALL: Get entire inventory entries direct from database (no search) according in sequence alphabetical order
@router.get("/getlist",
            response_model=list[EntryInventoryOut],
            status_code=200,
            summary="Get all entries from the inventory",
            description="This endpoint is used to get all entries from the inventory. It returns a list of entries.",
            response_model_exclude_unset=True,
)
async def get_all_entire_inventory(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """Get all inventory items"""
    try:
        items = await service.get_all_entries(db, skip, limit)
        logger.info(f"Retrieved {len(items)} inventory items")
        return items
    except Exception as e:
        logger.error(f"Error fetching inventory items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#  Search inventory items by various criteria {Product ID, Inventory ID, Project ID}
@router.get(
    "/search/",
    response_model=List[EntryInventoryOut],
    status_code=200,
    summary="Search inventory items",
    description="Search inventory items by Inventory ID, Product ID, or Project ID (exactly one required)",
    response_model_exclude_unset=True,
)
async def search_inventory(
    inventory_id: Optional[str] = Query(None, description="Inventory ID to search for"),
    product_id: Optional[str] = Query(None, description="Product ID to search for"),
    project_id: Optional[str] = Query(None, description="Project ID to search for"),
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """
    Search inventory items by exactly one of:
    - Inventory ID
    - Product ID
    - Project ID
    """
    try:
        # Convert empty strings to None
        inventory_id = inventory_id if inventory_id else None
        product_id = product_id if product_id else None
        project_id = project_id if project_id else None

        # Validate exactly one search parameter is provided
        provided_params = [p for p in [inventory_id, product_id, project_id] if p is not None]
        if len(provided_params) != 1:
            raise HTTPException(
                status_code=400,
                detail="Exactly one search parameter (inventory_id, product_id, or project_id) must be provided"
            )

        search_params = EntryInventorySearch(
            inventory_id=inventory_id,
            product_id=product_id,
            project_id=project_id
        )
        
        results = await service.search_entries(db, search_params)
        if not results:
            raise HTTPException(status_code=404, detail="No matching items found")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during search")
    
    
# UPDATE: Update an existing inventory entry
@router.put("/update/{inventory_id}",
            response_model=EntryInventoryOut,
            status_code=200,
            summary="Update an entry in the inventory",
            description="This endpoint is used to update an entry in the inventory. It takes a inventory_id and a JSON payload with the updated fields and values, and returns the updated entry.",
            response_model_exclude_unset=True,
)
async def update_inventory_item(
    inventory_id: str,
    update_data: EntryInventoryUpdate,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """
    Update inventory item by inventory_id.
    Immutable fields (uuid, sno, inventory_id, product_id, created_at) cannot be changed.
    """
        
    updated_entry = await service.update_entry(db, inventory_id, update_data)
    if not updated_entry:
        raise HTTPException(
            status_code=404,
            detail=f"Inventory item with ID {inventory_id} not found"
        )
    return updated_entry

# DELETE: Delete an inventory entry
@router.delete("/{inventory_id}", 
               status_code=200,
               summary="Delete an entry from the inventory",
               description="This endpoint is used to delete an entry from the inventory. It takes a UUID as a parameter and deletes the entry with the specified UUID.",
               )
async def delete_inventory_item(
    inventory_id: str,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """Delete an inventory item and return a confirmation message"""
    try:
        # Fetch the item to be deleted first
        item_to_delete = await service.get_by_inventory_id(db, inventory_id)
        if not item_to_delete:
            raise HTTPException(status_code=404, detail="Inventory item not found")

        # Perform the delete operation
        success = await service.delete_entry(db, inventory_id)
        if not success:
            raise HTTPException(status_code=404, detail="Inventory item not found")

        # Return a confirmation message with the deleted data
        return {"message": "Inventory item deleted successfully", "deleted_item": item_to_delete}

    except Exception as e:
        logger.error(f"Error deleting inventory item {inventory_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
# READ ALL: Get all inventory entries
@router.get("/entries",
            response_model=list[EntryInventoryOut],
            status_code=200,
            summary="List all entries from the inventory",
            description="This endpoint is used to list all entries from the inventory. It returns a list of entries.",
            response_model_exclude_unset=True,
            )
async def list_all_entries(
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """List all EntryInventory items (async version)."""
    try:
        # Fetch all the entries from the database
        entry_inventories = await service.list_entry_inventories_curd(db)
        # Log the number of retrieved entries
        logger.info(f"Retrieved {len(entry_inventories)} EntryInventories.")
        
        return entry_inventories
    except Exception as e:
        logger.error(f"Error in listing entry inventories: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
