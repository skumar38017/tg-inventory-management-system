#  backend/app/routers/to_event_routes.py
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
    ToEventRedisUpdate,
)
from backend.app.curd.to_event_inventry_curd import ToEventInventoryService
from backend.app.interface.to_event_interface import ToEventInventoryInterface

# Dependency to get the to_event service
def get_to_event_service() -> ToEventInventoryService:
    return ToEventInventoryService()

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
)
async def upload_to_event_data(
    db: AsyncSession = Depends(get_async_db),
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        logger.info("Starting Redis to database upload process")
        
        # Get data from service
        inventory_items = await service.upload_to_event_inventory(db)
        
        # Prepare response
        results = []
        for item in inventory_items:
            # Ensure we have proper timestamps
            created_at = item.created_at if hasattr(item, 'created_at') else datetime.now(timezone.utc)
            updated_at = item.updated_at if hasattr(item, 'updated_at') else datetime.now(timezone.utc)
            
            # Handle both ToEventRedisOut and direct database models
            project_id = getattr(item, 'project_id', None)
            if not project_id and hasattr(item, 'id'):
                project_id = item.id
                
            results.append({
                "success": True,
                "message": "Upload successful",
                "project_id": project_id,
                "inventory_items_count": len(getattr(item, 'inventory_items', [])),
                "created_at": created_at,
                "updated_at": updated_at,
                # Explicitly omit cretaed_at unless present in data
                **({'cretaed_at': item.cretaed_at} if hasattr(item, 'cretaed_at') else {})
            })
            
        logger.info(f"Successfully processed {len(results)} items")
        return results
        
    except ValidationError as ve:
        logger.error(f"Data validation error: {ve}")
        raise HTTPException(
            status_code=422,
            detail={"message": "Data validation failed", "errors": ve.errors()}
        )

# ----------------------------------------------------------------------------------------

# CREATE: Add a new to_event entry inventory store in directly in redis
@router.post("/to_event-create-item/",
    response_model=ToEventRedisOut,
    status_code=201,  # Changed to 201 for resource creation
    summary="Create a new inventory entry in Redis",
    description="Creates a new inventory entry stored directly in Redis. Returns the created entry with all fields.",
    response_model_exclude_none=True,  # Changed from exclude_unset to exclude_none
    tags=["Inventory (Redis)"]
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
    response_model=ToEventRedisOut,  # Changed from List[ToEventRedisOut]
    status_code=200,
    summary="Search project in local Redis by project_id",
    description="This endpoint searches for a project in local Redis by project_id and returns the complete project data.",
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
    response_model=ToEventRedisOut,
    status_code=200,
    summary="Update all project fields in Redis",
    description="Update any field of an existing project in Redis including all inventory item fields",
)
async def update_project_in_redis(
    project_id: str,
    update_data: ToEventRedisUpdate,
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        # Validate project_id format
        if not re.match(r'^PRJ\d+$', project_id):
            raise HTTPException(
                status_code=422,
                detail="Project ID must be in format PRJ followed by numbers"
            )

        # Get existing data
        existing_data = await service.get_project_data(project_id)
        if not existing_data:
            raise HTTPException(
                status_code=404,
                detail=f"Project {project_id} not found in Redis"
            )

        # Convert existing data to dict
        existing_dict = existing_data.model_dump()
        
        # Convert update data to dict, excluding unset fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Special handling for inventory items
        if 'inventory_items' in update_dict:
            if update_dict['inventory_items'] is None:
                # Clear inventory if explicitly set to None
                existing_dict['inventory_items'] = []
            else:
                # Replace inventory items entirely
                existing_dict['inventory_items'] = update_dict['inventory_items']
        
        # Update all other fields
        for field in update_dict:
            if field != 'inventory_items':
                existing_dict[field] = update_dict[field]
        
        # Always update the timestamp
        existing_dict['updated_at'] = datetime.now(timezone.utc)
        
        # Handle the 'cretaed_at' typo if present
        if 'cretaed_at' in existing_dict:
            existing_dict['created_at'] = existing_dict.pop('cretaed_at')
        
        # Validate the merged data
        updated_data = ToEventRedisOut(**existing_dict)
        
        # Save to Redis
        await service.update_project_data(project_id, updated_data)
        
        return updated_data
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=422, detail="Invalid data format")
    except Exception as e:
        logger.error(f"Update error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error updating project: {str(e)}"
        )