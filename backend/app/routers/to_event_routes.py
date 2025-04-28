#  backend/app/routers/to_event_routes.py
from backend.app.database.redisclient import get_redis_dependency
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
import logging
import re
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, date, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from backend.app.database.database import get_async_db
from datetime import datetime
from pydantic import ValidationError
from backend.app.schema.to_event_inventry_schma import (
    ToEventInventoryCreate,
    ToEventInventoryUpdate,
    ToEventInventoryOut,
    ToEventInventoryBase,
    ToEventInventorySearch,
    ToEventUploadResponse,
    ToEventRedis,
    ToEventRedisOut,
    ToEventRedisUpdateOut,
    ToEventRedisUpdateIn
)
from backend.app.curd.to_event_inventry_curd import ToEventInventoryService
from backend.app.interface.to_event_interface import ToEventInventoryInterface
from backend.app.interface.inventory_updater_interface import InventoryUpdaterInterface

# Dependency to get the to_event service
def get_to_event_service(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> ToEventInventoryService:
    return ToEventInventoryService(redis)

# Set up the router
router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --------------------------
# Asynchronous Endpoints
# --------------------------


#  Upload all `to_event_inventory` entries from local Redis to the database after click on `upload data` button
@router.post(
    "/to_event-upload-data/",
    response_model=List[ToEventUploadResponse],
    status_code=200,
    summary="Upload all entries from Redis to database",
    description="Uploads all to_event_inventory entries from local Redis to the database",
    tags=["Upload Inventory (DataBase)"]
)
async def upload_to_event_data(
    db: AsyncSession = Depends(get_async_db),
    service: ToEventInventoryService = Depends(get_to_event_service)
) -> List[ToEventUploadResponse]:
    """
    Upload all to_event_inventory entries from Redis to the database.
    
    Returns:
        List of ToEventUploadResponse objects with upload status for each project
    """
    try:
        logger.info("Starting Redis to database upload process")
        
        # Get data from service
        uploaded_items = await service.upload_to_event_inventory(db)
        
        if not uploaded_items:
            logger.warning("No inventory items found in Redis for upload")
            raise HTTPException(
                status_code=404,
                detail="No to_event inventory items found in Redis"
            )
        
        # Convert service response to proper output format
        results = []
        for item in uploaded_items:
            # Handle both direct objects and Pydantic models
            if isinstance(item, dict):
                item_data = item
            else:
                item_data = item.model_dump() if hasattr(item, 'model_dump') else dict(item)
            
            # Ensure required fields are present
            if 'project_id' not in item_data:
                logger.warning(f"Skipping item missing project_id: {item_data}")
                continue
                
            results.append(ToEventUploadResponse(
                success=True,
                message=item_data.get('message', 'Upload successful'),
                project_id=item_data['project_id'],
                inventory_items_count=item_data.get('inventory_items_count', 0),
                created_at=item_data.get('created_at', datetime.now(timezone.utc)),
                updated_at=item_data.get('updated_at', datetime.now(timezone.utc))
            ))
        
        logger.info(f"Successfully processed {len(results)} items")
        return results
        
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
            detail=f"Failed to upload to_event inventory data: {str(e)}"
        )

# ----------------------------------------------------------------------------------------

# CREATE: Add a new to_event entry inventory store in directly in redis
@router.post("/to_event-create-item/",
    response_model=ToEventRedisOut,
    status_code=201,  # Changed to 201 for resource creation
    summary="Create a new inventory entry in Redis",
    description="Creates a new inventory entry stored directly in Redis. Returns the created entry with all fields.",
    response_model_exclude_none=True,  # Changed from exclude_unset to exclude_none
    tags=["create Inventory (Redis)"]
)
async def create_inventory_item_route(
    item: ToEventInventoryCreate,
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        logger.info(f"New inventory creation request received for project: {item.project_id}")
        
        # Remove db parameter since we're storing in Redis directly
        created_item = await service.create_to_event_inventory(item)
        
        logger.info(f"Successfully created inventory in Redis for project: {item.project_id}")
        return created_item
        
    except ValueError as e:
        logger.warning(f"Validation error creating inventory: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating inventory: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create inventory in Redis. Please try again."
        )
    
# Load submitted from local redis
@router.get("/to_event-load-submitted-project-redis/",
    response_model=List[ToEventRedisOut],
    status_code=200,
    summary="Load submitted projects from Redis",
    description="This endpoint retrieves submitted projects directly from Redis with pagination support.",
    response_model_exclude_unset=True,
    tags=["load Inventory (Redis)"]
)
async def load_submitted_project_from_redis(
    skip: int = Query(0, description="Number of items to skip for pagination"),
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        logger.info(f"Loading submitted projects from Redis, skip={skip}")
        projects = await service.load_submitted_project_from_redis(skip)
        return projects
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading projects from Redis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
# Search project data project directly in local Redis  via `project_id`
@router.get("/to_event-search-entries-by-project-id/{project_id}/",
    response_model=ToEventRedisOut,  
    status_code=200,
    summary="Search project in local Redis by project_id",
    description="This endpoint searches for a project in local Redis by project_id and returns the complete project data.",
    tags=["search Inventory (Redis)"]
)
async def search_by_project_id(
    project_id: str,
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        logger.info(f"Searching project by project_id: {project_id}")
        
        # Call the service to get project data
        project_data = await service.get_project_data(project_id)
        
        if not project_data:
            raise HTTPException(
                status_code=404,
                detail=f"No project found for project_id: {project_id}"
            )
        
        logger.debug(f"Returning project data: {project_data.json()}")
        return project_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching project: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Error processing request: {str(e)}"
        )
    
# Upadte project according to `project_id` in local Redis 
@router.put(
    "/to_event-update-submitted-project-db/{project_id}/",
    response_model=ToEventRedisUpdateOut,
    status_code=200,
    summary="Update all project fields in Redis",
    description="Update any field of an existing project in Redis including all inventory item fields",
    tags=["update Inventory (Redis)"]
)
async def update_project_in_redis(
    project_id: str,
    update_data: ToEventRedisUpdateIn,
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        # Perform update - no need to check project_id in body since it's not in input schema
        updated_project = await service.update_project_data(project_id, update_data)
        return updated_project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))