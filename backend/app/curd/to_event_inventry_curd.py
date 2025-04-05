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
    ToEventInventorySearch,
    ToEventInventoryUpload,
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
import redis.asyncio as redis
from typing import List, Optional
from fastapi import HTTPException
from pydantic import ValidationError
import json
from backend.app.utils.barcode_generator import BarcodeGenerator  # Import the BarcodeGenerator class


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

class ToEventInventoryService(ToEventInventoryInterface):
    def __init__(self, base_url: str = config.BASE_URL):
        self.base_url = base_url
        self.barcode_generator = BarcodeGenerator()

    # Upload all `to_event_inventory` entries from local Redis to the database after click on `upload data` button
    async def upload_to_event_inventory(self, db: AsyncSession, skip: int = 0) -> List[ToEventRedisOut]:
        try:
            redis_keys = await redis_client.keys("to_event_inventory:*")
            uploaded_entries = []

            for key in redis_keys:
                try:
                    redis_data = await redis_client.get(key)
                    entry_data = json.loads(redis_data)

                    # Handle empty image URLs
                    if entry_data.get('project_barcode_image_url') == '':
                        entry_data['project_barcode_image_url'] = None

                    redis_entry = ToEventRedisOut(**entry_data)

                    # Try to update existing record first
                    existing = await db.execute(
                        select(ToEventInventory)
                        .where(ToEventInventory.uuid == redis_entry.uuid)
                    )
                    existing = existing.scalar_one_or_none()

                    if existing:
                        # Update logic
                        for field, value in redis_entry.dict().items():
                            if hasattr(existing, field) and field != "uuid":
                                setattr(existing, field, value)
                    else:
                        # Insert new record with error handling
                        try:
                            new_entry = ToEventInventory(**redis_entry.dict())
                            db.add(new_entry)
                            await db.flush()  # Test the insert immediately
                        except Exception as e:
                            logger.warning(f"Skipping duplicate entry {redis_entry.uuid}: {str(e)}")
                            continue
                        
                    uploaded_entries.append(redis_entry)

                except Exception as e:
                    logger.error(f"Error processing {key}: {str(e)}")
                    continue

            await db.commit()
            return sorted(uploaded_entries, key=lambda x: x.name or "")

        except SQLAlchemyError as e:
            logger.error(f"Database error during upload: {e}")
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error during upload")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload data from Redis")
    

# ------------------------------------------------------------------------------------------------
    #  Create new entry of inventory for to_event which is directly stored in redis
    async def create_to_event_inventory(self, db: AsyncSession, to_event_inventory: ToEventInventoryCreate):
        try:
            # Convert to dict and clean data
            inventory_data = to_event_inventory.model_dump()
            # self._normalize_inventory_data(inventory_data)

            # Ensure UUID is generated if missing
            if 'uuid' not in inventory_data or not inventory_data['uuid']:
                inventory_data['uuid'] = str(uuid.uuid4())  # Ensure UUID is set

            # Generate UUID and timestamps
            current_time = datetime.now(timezone.utc).isoformat()
            inventory_data.update({
                'created_at': current_time,
                'updated_at': current_time
            })

            # Generate barcodes
            barcode, unique_code = self.barcode_generator.generate_linked_codes(inventory_data)

            # Update inventory data with barcode information
            inventory_data['project_barcode'] = barcode
            inventory_data['project_barcode_unique_code'] = unique_code

            # Create Redis entry
            redis_entry = ToEventRedis(
                uuid=inventory_data['uuid'],
                sno=inventory_data['sno'],
                project_id=inventory_data['project_id'],
                employee_name=inventory_data['employee_name'],
                location=inventory_data['location'],
                client_name=inventory_data['client_name'],
                setup_date=inventory_data['setup_date'],
                project_name=inventory_data['project_name'],
                event_date=inventory_data['event_date'],
                zone_active=inventory_data['zone_active'],
                name=inventory_data['name'],
                description=inventory_data['description'],
                quantity=inventory_data['quantity'],
                material=inventory_data['material'],
                comments=inventory_data['comments'],
                total=inventory_data['total'],
                unit=inventory_data['unit'],
                per_unit_power=inventory_data['per_unit_power'],
                total_power=inventory_data['total_power'],
                status=inventory_data['status'],
                poc=inventory_data['poc'],
                submitted_by=inventory_data['submitted_by'],
                created_at=inventory_data['created_at'],
                updated_at=inventory_data['updated_at'],
                project_barcode=inventory_data['project_barcode'],
                project_barcode_unique_code=inventory_data['project_barcode_unique_code'],
                project_barcode_image_url=inventory_data.get('project_barcode_image_url', '')
            )

            # Store Redis entry
            await redis_client.set(
                f"to_event_inventory:{redis_entry.project_id}", 
                redis_entry.json()
            )

            logger.info(f"Stored in Redis - Project ID: {redis_entry.project_id}")
            return redis_entry

        except Exception as e:
            logger.error(f"Redis storage failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create inventory: {str(e)}")
    
    #  show all project directly from local Redis in `submitted Forms` directly after submitting the form
    async def load_submitted_project_from_db(self, db: AsyncSession, skip: int = 0) -> List[ToEventRedisOut]:
        try:
            result = await db.execute(
                select(ToEventInventory)
                .order_by(ToEventInventory.updated_at)
                .offset(skip)
            )
            items = result.scalars().all()
            return [ToEventRedisOut.model_validate(item) for item in items] 
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching entries: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    async def search_entries_by_project_id(
        self,
        db: AsyncSession,
        search_filter: ToEventInventorySearch
    ) -> List[ToEventRedisOut]:
        try:
            project_id = search_filter.project_id
            if not project_id:
                raise ValueError("Project ID is required")

            # Check Redis first
            redis_key = f"project:{project_id}"
            redis_data = await redis_client.get(redis_key)

            if redis_data:
                try:
                    redis_items = json.loads(redis_data)
                    if isinstance(redis_items, list):
                        return [ToEventRedisOut.model_validate(item) for item in redis_items]
                    return [ToEventRedisOut.model_validate(json.loads(redis_data))]
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.error(f"Invalid Redis data for {redis_key}: {e}")
                    # Fall through to DB query

            # Fallback to database
            result = await db.execute(
                select(ToEventInventory).where(ToEventInventory.project_id == project_id)
            )
            items = result.scalars().all()

            # Convert to RedisOut format and serialize properly
            db_items = [ToEventRedisOut.model_validate(item).model_dump() for item in items]

            # Cache with proper JSON serialization
            if db_items:
                await redis_client.set(
                    redis_key,
                    json.dumps(db_items, default=str),  # Use default=str for dates
                    ex=3600
                )

            return [ToEventRedisOut.model_validate(item) for item in db_items]

        except Exception as e:
            logger.error(f"Error in service during search: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

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
        

        
# # Dependency function
# def get_to_event_service():
#     return ToEventInventoryService()