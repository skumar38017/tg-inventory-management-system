# backend/app/routers/entry_inventory_routes.py
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from backend.app.database.database import get_async_db
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryCreate,
    EntryInventoryUpdate,
    EntryInventoryOut,
    EntryInventorySearch,
    DateRangeFilter
)
from backend.app.curd.entry_inverntory_curd import EntryInventoryService
from backend.app.interface.entry_inverntory_interface import EntryInventoryInterface

# Dependency to get the entry inventory service
def get_entry_inventory_service() -> EntryInventoryInterface:
    return EntryInventoryInterface()

# Set up the router
router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --------------------------
# Asynchronous Endpoints
# --------------------------

#  Refrech record in UI and show all updated data directly 
@router.get("/refresh/",
            response_model=EntryInventoryOut,
            status_code=200,
            summary="Refresh an entry in the inventory",
            description="This endpoint is used to refresh an entry in the inventory. It takes a UUID as a parameter and returns the updated entry.",
            response_model_exclude_unset=True,
            )
async def refresh_inventory_item_route(db: AsyncSession = Depends(get_async_db), service: EntryInventoryService = Depends(get_entry_inventory_service)):
    refresh_data=await service.list_entry_inventories_curd(db)
    if not refresh_data:
        raise HTTPException(status_code=404, detail="EntryInventory not found")
    return refresh_data

# CREATE: Add a new entry to the inventory
@router.post("/create/",
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
    """Create a new inventory item"""
    try:
        new_item = await service.create_entry_inventory_curd(db, item)
        if not new_item:
            raise HTTPException(status_code=400, detail="Failed to create inventory item")
        return new_item
    except Exception as e:
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# READ: Get an inventory entry by its inventory_id
@router.get("/fetch/{inventory_id}",
            response_model=EntryInventoryOut,
            status_code=200,
            summary="Get an entry from the inventory by its inventory_id",
            description="This endpoint is used to get an entry from the inventory by its inventory_id. It takes a inventory_id as a parameter and returns the entry with the specified inventory_id.",
            response_model_exclude_unset=True,
)
async def get_inventory_item_route(inventory_id: str, db: AsyncSession = Depends(get_async_db), service: EntryInventoryService = Depends(get_entry_inventory_service)):
    entry_inventory = await service.get_entry_inventory_by_inventry_id_interface(db, inventory_id=inventory_id)
    if not entry_inventory:
        raise HTTPException(status_code=404, detail="EntryInventory not found")
    return entry_inventory

# READ ALL: Get all inventory entries
@router.get("/getlist",
            response_model=list[EntryInventoryOut],
            status_code=200,
            summary="Get all entries from the inventory",
            description="This endpoint is used to get all entries from the inventory. It returns a list of entries.",
            response_model_exclude_unset=True,
)
async def get_all_entire_inventory_route(
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """Get all inventory items"""
    try:
        items = await service.get_all_entry_inventory_curd(db)
        logger.info(f"Retrieved {len(items)} inventory items")
        return items
    except Exception as e:
        logger.error(f"Error fetching inventory items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#  Search inventory items by various criteria
@router.get(
    "/search/{inventory_id}",
    response_model=List[EntryInventoryOut],
    status_code=200,
    summary="Search inventory items",
    description="Search inventory items by various criteria",
    response_model_exclude_unset=True,
)
async def search_inventory_route(
    inventory_id: str,  # This should be a path parameter
    product_id: Optional[str] = Query(None, description="Product ID to search for"),
    project_id: Optional[str] = Query(None, description="Project ID to search for"),
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """Search inventory items by various criteria"""
    try:
        search_params = EntryInventorySearch(
            inventory_id=inventory_id,  # Path param
            product_id=product_id,
            project_id=project_id
        )
        results = await service.search_inventory_interface(db, search_params)
        if not results:
            raise HTTPException(status_code=404, detail="No matching items found")
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
#  Filter inventory by date range
@router.get(
    "/date-range",
    response_model=List[EntryInventoryOut],
    status_code=200,
    summary="Filter inventory by date range",
    description="Get inventory items within a specific date range",
    response_model_exclude_unset=True,
)
async def get_inventory_by_date_range_route(
    from_date: str,
    to_date: str,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """Get inventory items within a date range"""
    try:
        date_filter = DateRangeFilter(
            from_date=datetime.strptime(from_date, "%Y-%m-%d"),
            to_date=datetime.strptime(to_date, "%Y-%m-%d")
        )
        results = await service.get_entry_inventory_by_date_range_curd(db, date_filter)
        if not results:
            raise HTTPException(status_code=404, detail="No items found in date range")
        return results
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Date range filter failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    #  -------------------------------------------------------------------------------------------


# UPDATE: Update an existing inventory entry
@router.put("/update/{inventory_id}",
            response_model=EntryInventoryOut,
            status_code=200,
            summary="Update an entry in the inventory",
            description="This endpoint is used to update an entry in the inventory. It takes a inventory_id and a JSON payload with the updated fields and values, and returns the updated entry.",
            response_model_exclude_unset=True,
)
async def update_inventory_item_route(uuid: str, entry_inventory_update: EntryInventoryUpdate, db: AsyncSession = Depends(get_async_db), service: EntryInventoryService = Depends(get_entry_inventory_service)):
    updated_entry = await service.update_inventory_item_curd(db, uuid, entry_inventory_update)
    if not updated_entry:
        raise HTTPException(status_code=404, detail="EntryInventory not found")
    return updated_entry

# DELETE: Delete an inventory entry
@router.delete("/{inventory_id}", 
               status_code=200,  # You can still use 200 OK
               summary="Delete an entry from the inventory",
               description="This endpoint is used to delete an entry from the inventory. It takes a UUID as a parameter and deletes the entry with the specified UUID.",
               )
async def delete_inventory_item_route(
    inventory_id: str,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """Delete an inventory item and return a confirmation message"""
    try:
        # Fetch the item to be deleted first
        item_to_delete = await service.get_entry_inventory_by_inventry_id_interface(db, inventory_id)
        if not item_to_delete:
            raise HTTPException(status_code=404, detail="Inventory item not found")

        # Perform the delete operation
        success = await service.delete_inventory_iten_curd(db, inventory_id)
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
async def list_entry_inventories_route(db: AsyncSession = Depends(get_async_db), service: EntryInventoryService = Depends(get_entry_inventory_service)):
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
