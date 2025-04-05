#  backend/app/routers/to_event_routes.py
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, date, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from backend.app.database.database import get_async_db
from datetime import datetime
from backend.app.schema.to_event_inventry_schma import (
    ToEventInventoryCreate,
    ToEventInventoryUpdate,
    ToEventInventoryOut,
    ToEventInventoryBase,
    ToEventInventoryUpdateOut,
    ToEventInventoryUpload,
    ToEventInventorySearch,
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
@router.post("/to_event-upload-data/",
    response_model=List[ToEventRedisOut],
    status_code=200,
    summary="Upload all entries from Redis to database",
    description="Uploads all to_event_inventory entries from local Redis to the database",
)
async def upload_inventory_item_route(
    db: AsyncSession = Depends(get_async_db),
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        logger.info("Upload request received")
        return await service.upload_to_event_inventory(db)
    except Exception as e:
        logger.error(f"Error uploading inventory items: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ----------------------------------------------------------------------------------------

# CREATE: Add a new to_event entry inventory store in directly in redis
@router.post("/to_event-create-item/",
    response_model=ToEventRedisOut,
    status_code=200,
    summary="Create a new entry in the inventory",
    description="This endpoint is used to create a new entry in the inventory. It takes a JSON payload with the necessary fields and values, and returns the created entry.",
    response_model_exclude_unset=True,
)
async def create_inventory_item_route(
    item: ToEventInventoryCreate,
    db: AsyncSession = Depends(get_async_db),
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        logger.info(f"New item creation request received")
        return await service.create_to_event_inventory(db, item)
    except Exception as e:
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
# Load submitted from local redis
@router.get("/to_event-load-submitted-project-db/",
    response_model=List[ToEventRedisOut],
    status_code=200,
    summary="Load submitted projects from database",
    description="This endpoint retrieves submitted projects from the database with pagination support.",
    response_model_exclude_unset=True,
)
async def load_submitted_project(
    skip: int = Query(0, description="Number of items to skip for pagination"),
    db: AsyncSession = Depends(get_async_db),
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        logger.info(f"Loading submitted projects from database, skip={skip}")
        return await service.load_submitted_project_from_db(db, skip)
    except Exception as e:
        logger.error(f"Error loading projects: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
# Search all project directly in local Redis  before submitting the form
@router.get("/to_event-search-entries-by-project-id/{project_id}/",
    response_model=List[ToEventRedisOut],
    status_code=200,
    summary="Search all entries in local Redis by project_id",
    description="This endpoint searches all entries in local Redis by project_id and returns the results.",
    response_model_exclude_unset=True,
)
async def search_by_project_id(
    project_id: str ,
    db: AsyncSession = Depends(get_async_db),
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        logger.info(f"Searching entries by project_id: {project_id}")
        
        # Use the search-specific schema
        search_filter = ToEventInventorySearch(project_id=project_id)
        
        # Call the service to search entries by project_id
        entries = await service.search_entries_by_project_id(db, search_filter)
        
        return entries
        
    except Exception as e:
        logger.error(f"Error searching entries by project_id: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Upadte project according to `project_id` in local Redis 
@router.put("/to_event-update-submitted-project-db/{project_id}/",
            status_code=200,
            summary="Update an existing entry in the inventory",
            description="This endpoint is used to update an existing entry in the inventory. It takes a JSON payload with the necessary fields and values, and returns the updated entry.",
            response_model=ToEventRedisOut,
            response_model_exclude_unset=True,
            )
async def update_to_event_project_item(
    project_id: str,
    update_data: ToEventRedisUpdate,
    db: AsyncSession = Depends(get_async_db),
    service: ToEventInventoryService = Depends(get_to_event_service)
):
    try:
        # Convert update_data to dict and add updated_at if not provided
        update_dict = update_data.dict(exclude_unset=True)
        if 'updated_at' not in update_dict:
            update_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
            
        updated_item = await service.update_to_event_project(
            project_id=project_id,
            update_data=ToEventRedisUpdate(**update_dict)  # Recreate with updated timestamp
        )
        return updated_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))