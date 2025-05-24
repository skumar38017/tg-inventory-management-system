# backend/app/routers/entry_inventory_routes.py
from app.utils.common_imports import *

from app.schema.entry_inventory_schema import (
    EntryInventoryCreate,
    EntryInventoryUpdate,
    EntryInventoryOut,
    InventoryRedisOut,
    DateRangeFilter,
    InventoryRedisOut
)
from fastapi import Depends, Request
from app.curd.entry_inverntory_curd import EntryInventoryService
from app.curd.google_sheet_redis_inventory import GoogleSheetsToRedisSyncService
from app.interface.entry_inverntory_interface import (
    EntryInventoryInterface
)

# Dependency to get the entry inventory service
def get_entry_inventory_service(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> EntryInventoryService:
    return EntryInventoryService(redis)

# Dependency to get the entry inventory service
def get_entryget_inventory_from_google_sheet(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> GoogleSheetsToRedisSyncService:
    return GoogleSheetsToRedisSyncService(redis)

# Set up the router
router = APIRouter()

# --------------------------
# Asynchronous Endpoints
# --------------------------

# Refrech record in UI and show all updated data directly after clicking {sync} button [/sync/]
@router.post("/sync-from-sheets/",
    response_model=List[InventoryRedisOut],
    status_code=200,
    summary="Sync inventory from Google Sheets",
    description="Fetch inventory data from Google Sheets and store in Redis",
    response_model_exclude_unset=True,
    responses={
        200: {"description": "Successfully synced with Redis"},
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error during sync"}
    },
    tags=["Sync Inventory (Redis)"]
)
async def sync_from_sheets(
    request: Request,
    service: GoogleSheetsToRedisSyncService = Depends(get_entryget_inventory_from_google_sheet)
):
    """
    Synchronize inventory data from Google Sheets to Redis cache.
    
    This endpoint will:
    1. Authenticate with Google using sumitkumar@tagglabs.in
    2. Fetch all inventory entries from the Google Sheet
    3. Store them in Redis with proper serialization
    4. Return the list of synced items
    """
    try:
        inventory_type = 'inventory'

        logger.info("Starting Google Sheets sync operation")
        synced_items = await service.sync_inventory_from_google_sheets(request, inventory_type=inventory_type)
        
        if not synced_items:
            logger.warning("Google Sheets sync completed with no items")
            return []
            
        logger.info(f"Google Sheets sync completed with {len(synced_items)} items")
        return synced_items
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Critical error during Google Sheets sync: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to sync with Google Sheets"
        )

#  Upload/update all inventory entries from local Redis to the database after click on upload data button
@router.post(
    "/Upload-entry-inventory/",
    response_model=List[InventoryRedisOut],
    status_code=200,
    summary="Upload all entries from Redis to database",
    description="Uploads all inventory entries from local Redis to the database",
    tags=["Upload Inventory (DataBase)"]
)
async def upload_inventory_data(
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """
    Upload all inventory entries from Redis to the database.
    
    Returns:
        List of InventoryRedisOut objects with upload status for each item
    """
    try:
        logger.info("Starting Redis to database upload process")
        
        # Get data from service
        uploaded_items = await service.upload_entry_inventory(db)
        
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

# -------------------------------------------------------------------------------------------------
# Show all inventory entries directly from local Redis Database  (no search) according in sequence alphabetical order after clicking `Show All` button
@router.get("/show-all/",
    response_model=List[InventoryRedisOut],
    status_code=200,
    summary="Show all Redis-cached inventory",
    description="Retrieves all inventory entries from Redis cache sorted alphabetically by inventory_name",
    responses={
        200: {"description": "Successfully retrieved cached data"},
        404: {"description": "No cached data found"},
        500: {"description": "Internal server error during retrieval"}
    },
    tags=["Show all Inventory (Redis)"]
)
async def show_all_redis(
    skip: int = 0,
    limit: int = 1000,  # Add pagination limit
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """
    Retrieve all inventory data from Redis cache sorted alphabetically.
    
    This endpoint will:
    1. Fetch all cached inventory entries from Redis
    2. Validate and deserialize the data
    3. Sort alphabetically by inventory_name
    4. Apply pagination (skip and limit)
    5. Return the sorted list of inventory items
    """
    try:
        logger.info("Fetching all inventory data from Redis")
        
        # Get all entries from Redis
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
        
        # Sort alphabetically by inventory_name (case insensitive)
        cached_data.sort(key=lambda x: x.inventory_name.lower())
        
        # Apply pagination
        paginated_data = cached_data[skip : skip + limit]
        
        logger.info(f"Successfully retrieved {len(paginated_data)} cached entries (showing {skip} to {skip + limit})")
        return paginated_data
        
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
# -------------------------------------------------------------------------------------------------

#  Filter inventory from database by date range without passing any `IDs`
@router.get(
    "/date-range/",
    response_model=List[EntryInventoryOut],
    status_code=200,
    summary="Filter inventory by date range",
    description="Get inventory items within a specific date range",
    response_model_exclude_unset=True,
    tags=["Filter Inventory (Redis)"]
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

# CREATE: Add a new entry to the inventory
@router.post("/create-item/",
    response_model=EntryInventoryOut,  # Make sure this is EntryInventoryOut
    status_code=201,
    summary="Create a new entry in the inventory",
    description="This endpoint is used to create a new entry in the inventory. It takes a JSON payload with the necessary fields and values, and returns the created entry including the barcode image data.",
    response_model_exclude_unset=True,
    tags=["create Inventory (Redis)"]
)
async def create_inventory_item_route(
    item: EntryInventoryCreate,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    try:
        logger.info(f"Creating new inventory item")
        # Determine inventory type based on the item's properties
        inventory_type = "inventory"  # Default type for this endpoint
        return await service.create_entry_inventory(
            db=db,
            inventory_type=inventory_type,
            entry_data=item
        )
    except HTTPException:
        raise
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
            tags=["Get Inventory (Redis)"]
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

# READ: Get an inventory which is match from Inventory Name
@router.get("/load-record/{inventory_name}",
            response_model=EntryInventoryOut,
            status_code=200,
            summary="Get an entry from the inventory by its Inventory Name",
            description="This endpoint is used to get an entry from the inventory by its Inventory Name. It takes a Inventory Name as a parameter and returns the entry with the specified Inventory Name.",
            response_model_exclude_unset=True,
            tags=["Get Inventory (Redis)"]
)
async def get_inventory_item(
    inventory_name: str,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    entry_inventory = await service.get_by_inventory_name(db, inventory_name)
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
            tags=["Get Inventory (Redis)"]
)
async def get_all_entire_inventory(
    skip: int = 0,
    db: AsyncSession = Depends(get_async_db),
    service: EntryInventoryService = Depends(get_entry_inventory_service)
):
    """Get all inventory items"""
    try:
        items = await service.get_all_entries(db, skip)
        logger.info(f"Retrieved {len(items)} inventory items")
        return items
    except Exception as e:
        logger.error(f"Error fetching inventory items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#  Search inventory items by various criteria {Product ID, Inventory ID}
@router.get(
    "/search/",
    response_model=List[EntryInventoryOut],
    status_code=200,
    summary="Search Entry inventory items",
    description="Search inventory items by Inventory ID, Product ID, or Project ID (exactly one required)",
    response_model_exclude_unset=True,
    tags=["search Inventory (Redis)"]
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

        # Call service directly with the search parameters
        results = await service.search_entries(
            db,
            inventory_id=inventory_id,
            product_id=product_id,
            project_id=project_id
        )
        
        if not results:
            raise HTTPException(status_code=404, detail="No matching items found")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during search: {str(e)}"
        )   
    
# UPDATE: Update an existing inventory entry
@router.put("/update/{inventory_id}/",
            response_model=EntryInventoryOut,
            status_code=200,
            summary="Update an entry in the inventory",
            description="This endpoint is used to update an entry in the inventory. It takes a inventory_id and a JSON payload with the updated fields and values, and returns the updated entry.",
            response_model_exclude_unset=True,
            tags=["update Inventory (Redis)"]
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
    try:
        # Convert the update data to dict and remove any None values
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Remove any timestamp fields that might have been included
        update_dict.pop('created_at', None)
        update_dict.pop('updated_at', None)
        
        # Create a new update data object with the cleaned dict
        clean_update_data = EntryInventoryUpdate(**update_dict)
        
        updated_entry = await service.update_entry(db, inventory_id, clean_update_data)
        if not updated_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Inventory item with ID {inventory_id} not found"
            )
        return updated_entry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update inventory: {str(e)}"
        )

# DELETE: Delete an inventory entry
@router.delete("/delete/{inventory_id}",
               status_code=204,
               summary="Delete an inventory entry",
               description="Delete an inventory entry by ID",
               tags=["Delete Inventory (Redis)"]
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
            tags=["List Inventory (Redis)"]
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
