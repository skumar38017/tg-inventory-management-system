#  backend/app/curd/to_event_inventry_curd.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, time, timedelta, timezone
from backend.app.models.to_event_inventry_model import ToEventInventory
from backend.app.schema.to_event_inventry_schma import (
    ToEventInventoryCreate, 
    ToEventInventoryBase,
    ToEventInventoryOut,
    ToEventInventoryBase,
    ToEventInventoryUpdate,
    ToEventInventoryUpdateOut,
    ToEventRedis,
    ToEventRedisOut,
)
from sqlalchemy.exc import SQLAlchemyError
from backend.app.interface.to_event_interface import ToEventInventoryInterface
import logging
from fastapi import HTTPException
from typing import List, Optional
from backend.app.database.redisclient import redis_client
from backend.app import config
import uuid


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

class ToEventInventoryService(ToEventInventoryInterface):
    """Implementation of ToEventInventoryInterface with async operations"""
    def __init__(self, base_url: str = config.BASE_URL):
        self.base_url = base_url  # Your server's base URL

    #  Create new entry of inventory for to_event which is directly stored in redis
    #  Create new entry
    async def create_to_event_inventory(self, db: AsyncSession, to_event_inventory: ToEventInventoryCreate):
        if db is None:
            raise ValueError("Database session is None")

        try:
            # Convert Pydantic model to dictionary using .dict() method
            inventory_data = to_event_inventory.model_dump()

            # Handle field name variations
            if "even_date" in inventory_data:
                inventory_data["event_date"] = inventory_data.pop("even_date")
            if "Total" in inventory_data:
                inventory_data["total"] = inventory_data.pop("Total")
            if "per_uinit_power" in inventory_data:
                inventory_data["per_unit_power"] = inventory_data.pop("per_uinit_power")

            # Create new instance of ToEventInventory
            new_entry = ToEventInventory(**inventory_data)

            # Ensure UUID generation if not already present
            if not hasattr(new_entry, 'uuid') or not new_entry.uuid:
                new_entry.uuid = str(uuid.uuid4())

            # Set timestamps
            current_time = datetime.now(timezone.utc)
            new_entry.created_at = current_time
            new_entry.updated_at = current_time

            # Store in Redis as ToEventRedis format
            redis_entry = ToEventRedis(
                uuid=new_entry.uuid,
                sno=new_entry.sno,
                project_id=new_entry.project_id,
                employee_name=new_entry.employee_name,
                location=new_entry.location,
                client_name=new_entry.client_name,
                setup_date=new_entry.setup_date,
                project_name=new_entry.project_name,
                event_date=new_entry.event_date,
                zone_active=new_entry.zone_active,
                name=new_entry.name,
                description=new_entry.description,
                quantity=new_entry.quantity,
                material=new_entry.material,
                comments=new_entry.comments,
                total=new_entry.total,
                unit=new_entry.unit,
                per_unit_power=new_entry.per_unit_power,
                total_power=new_entry.total_power,
                status=new_entry.status,
                poc=new_entry.poc,
                submitted_by=new_entry.submitted_by,
                created_at=new_entry.created_at,
                updated_at=new_entry.updated_at,
                project_barcode=getattr(new_entry, 'project_barcode', ''),
                project_barcode_unique_code=getattr(new_entry, 'project_barcode_unique_code', ''),
                project_barcode_image_url=getattr(new_entry, 'project_barcode_image_url', '')
            )

            # Store the entry in Redis
            await redis_client.set(
                f"to_event_inventory:{new_entry.project_id}", 
                redis_entry.json()
            )

            logger.info(f"Stored entry in Redis with UUID: {new_entry.project_id}")
            return redis_entry
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create inventory: {str(e)}")
    
        
    #  show all project directly from local Redis in `submitted Forms` directly after submitting the form
    async def get_to_event_inventory(self, db: AsyncSession, skip: int = 0) -> List[ToEventRedisOut]:
        try:
            result = await db.execute(
                select(ToEventInventory)
                .order_by(ToEventInventory.name)  # Alphabetical order
                .offset(skip)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching entries: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    #  show all project directly from local Redis in `submitted Forms` directly after submitting the form
    async def get_project_by_project_id(self, db: AsyncSession, project_id: str) -> Optional[ToEventRedisOut]:
        try:
            result = await db.execute(
                select(ToEventInventory)
                .where(ToEventInventory.project_id == project_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching entry: {e}")
            raise HTTPException(status_code=500, detail="Database error")