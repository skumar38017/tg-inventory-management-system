#  backend/app/routers/to_event_routes.py
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, date
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
    ToEventRedis,
    ToEventRedisOut,
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
    response_model=ToEventRedis,
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