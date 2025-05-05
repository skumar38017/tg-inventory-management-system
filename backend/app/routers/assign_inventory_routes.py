# backend/app/routers/Assign_inventory_routes.py

from backend.app.utils.common_imports import *

from backend.app.schema.assign_inventory_schema import (
    AssignmentInventoryCreate,
    AssignmentInventoryUpdate,
    AssignmentInventoryRedisOut,
    RedisSearchResult
)
from backend.app.models.assign_inventory_model import AssignmentInventory
from backend.app.curd.assign_inventory_curd import AssignInventoryService

# Dependency to get the Assign inventory service
def get_Assign_inventory_service(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> AssignInventoryService:
    return AssignInventoryService(redis)

# Set up the router
router = APIRouter()

# --------------------------
# Asynchronous Endpoints
# --------------------------

# upload all assign_inventory entries from local Redis to the database after click on upload data button
@router.post(
    "/upload-assign-inventory/",
    response_model=List[AssignmentInventoryRedisOut],
    status_code=200,
    summary="Upload all assigned entries from Redis to database",
    description="Uploads all assign_inventory entries from local Redis to the database",
    tags=["Upload Inventory (DataBase)"]
)
async def upload_assign_inventory(
    db: AsyncSession = Depends(get_async_db),
    service: AssignInventoryService = Depends(get_Assign_inventory_service)
):
    """
    Upload all assign_inventory entries from Redis to the database.
    
    Returns:
        List of AssignmentInventoryRedisOut objects with upload status for each item
    """
    try:
        logger.info("Starting Redis to database upload process")
        
        # Get data from service
        uploaded_items = await service.upload_from_event_inventory(db)
        
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
@router.get("/show-all-assign-inventory/",
    response_model=List[AssignmentInventoryRedisOut],
    status_code=200,
    summary="Show all Redis-cached assigned inventory",
    description="Retrieves all inventory entries from Redis cache",
    responses={
        200: {"description": "Successfully retrieved cached data"},
        404: {"description": "No cached data found"},
        500: {"description": "Internal server error during retrieval"}
    },
    tags=["Show all Inventory (Redis)"]
)
async def show_assigned_inventory(
    service: AssignInventoryService = Depends(get_Assign_inventory_service)
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
        cached_data = await service.show_all_assigned_inventory_from_redis()
        
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

# CREATE: Add a new Assign to the inventory
@router.post("/create-assign-inventory/",
    response_model=AssignmentInventoryRedisOut,
    status_code=200,
    summary="Create a new Assign in the inventory",
    description="This endpoint is used to create a new Assign in the inventory. It takes a JSON payload with the necessary fields and values, and returns the created Assign.",
    response_model_exclude_unset=True,
    tags=["create Inventory (Redis)"]
)
async def create_inventory_item_route(
    item: AssignmentInventoryCreate,
    db: AsyncSession = Depends(get_async_db),
    service: AssignInventoryService = Depends(get_Assign_inventory_service)
):
    try:
        item_data = item.dict(exclude_unset=True)
        logger.info(f"New item created: {item_data}")
        return await service.create_assignment_inventory(db, item_data)
    except Exception as e:
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=400, detail=str(e))
# ________________________________________________________________________________________

# READ: search/fetch an inventory which is match from [Inventory ID, Project ID, Product ID, Employee name]
@router.get("/search-assigned-inventory/",
            response_model=List[RedisSearchResult],
            status_code=200,
            summary="Search assigned inventory by multiple fields",
            description="Search inventory assignments by inventory_id, project_id, product_id, or employee_name",
            response_model_exclude_unset=True,
            tags=["search Inventory (Redis)"]
)
async def search_assigned_inventory(
    inventory_id: Optional[str] = Query(None, description="Inventory ID to search for"),
    product_id: Optional[str] = Query(None, description="Product ID to search for"),
    project_id: Optional[str] = Query(None, description="Project ID to search for"),
    employee_name: Optional[str] = Query(None, description="Employee name to search for"),
    db: AsyncSession = Depends(get_async_db),
    service: AssignInventoryService = Depends(get_Assign_inventory_service)
):
    results = await service.search_entries_by_fields(
        db,
        inventory_id=inventory_id,
        project_id=project_id,
        product_id=product_id,
        employee_name=employee_name
    )
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="No matching inventory assignments found"
        )
    
    return results

# READ ALL: List current added Assigned inventory
@router.get("/list-added-assign-inventory/",
            response_model=list[AssignmentInventoryRedisOut],
            status_code=200,
            summary="Load assigned entries from the inventory",
            description="This endpoint is used to get all entries from the inventory. It returns a list of entries.",
            response_model_exclude_unset=True,
            tags=["load Inventory (Redis)"]
)
async def list_added_assigned_inventory(
    skip: int = 0,
    db: AsyncSession = Depends(get_async_db),
    service: AssignInventoryService = Depends(get_Assign_inventory_service)
):
    """Get all inventory items"""
    try:
        items = await service.list_added_assigned_inventory(db, skip)
        logger.info(f"Retrieved {len(items)} inventory items")
        return items
    except Exception as e:
        logger.error(f"Error fetching inventory items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#  update/edit existing Assigned Inventory by [InventoryID, EmployeeName]
@router.put(
    "/update-assigned-inventory/{employee_name}/{inventory_id}/",
    response_model=AssignmentInventoryRedisOut,
    status_code=200,
    summary="Update assigned inventory",
    description="Update inventory assignment by employee_name and inventory_id",
    response_model_exclude_unset=True,
    tags=["update Inventory (Redis)"]
)
async def update_assigned_inventory(
    employee_name: str,
    inventory_id: str,
    update_data: AssignmentInventoryUpdate,
    service: AssignInventoryService = Depends(get_Assign_inventory_service)
):
    """
    Update an inventory assignment by employee_name and inventory_id.
    Immutable fields (IDs, barcodes, timestamps) cannot be changed.
    """
    # Convert Pydantic model to dict and add path parameters
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict.update({
        'employee_name': employee_name,
        'inventory_id': inventory_id
    })
    
    return await service.update_assignment_inventory(update_dict)  

# DELETE: Delete an inventory Assigned
@router.delete(
    "/delete-assigned-inventory/{employee_name}/{inventory_id}/",
    status_code=200,
    response_model=AssignmentInventoryRedisOut,  # Define this model if needed
    summary="Delete assigned inventory",
    description="Delete an inventory assignment by employee name and inventory ID",
    tags=["Delete Inventory (Redis)"]
)
async def delete_assigned_inventory(
    employee_name: str,
    inventory_id: str,
    db: AsyncSession = Depends(get_async_db),
    service: AssignInventoryService = Depends(get_Assign_inventory_service)
):
    deleted = await service.delete_assigned_inventory(
        db=db,
        employee_name=employee_name,
        inventory_id=inventory_id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )
    
    return {"status": "success", "message": "Assignment deleted"}

# GET: Get inventory by inventory_id and employee_name
@router.get("/get-assigned-inventory/{employee_name}/{inventory_id}/",
            response_model=RedisSearchResult,
            status_code=200,
            summary="Get assigned inventory by employee name and inventory ID",
            description="Get inventory assignment by employee_name and inventory_id from Redis cache",
            response_model_exclude_unset=True,
            tags=["Get Inventory (Redis)"]
)
async def get_assigned_inventory_by_id(
    employee_name: str,
    inventory_id: str,
    service: AssignInventoryService = Depends(get_Assign_inventory_service)
):
    """Fetch inventory data by employee name and inventory ID from Redis"""
    try:
        logger.info(f"Fetching inventory for employee {employee_name} and inventory {inventory_id}")
        item = await service.get_assigned_inventory(employee_name, inventory_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Inventory assignment not found for employee {employee_name} and inventory {inventory_id}"
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching inventory")