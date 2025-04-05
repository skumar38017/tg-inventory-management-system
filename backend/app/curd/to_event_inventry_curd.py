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
    ToEventRedisUpdate,
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
    async def upload_to_event_inventory(self, db: AsyncSession) -> List[ToEventRedisOut]:
        try:
            # Get all relevant Redis keys
            inventory_keys = await redis_client.keys("to_event_inventory:*")
            project_keys = await redis_client.keys("project:*")
            all_keys = inventory_keys + project_keys

            if not all_keys:
                logger.info("No Redis entries found to upload")
                return []

            uploaded_entries = []
            success_count = 0
            error_count = 0
            processed_project_ids = set()

            for key in all_keys:
                try:
                    # Get and parse Redis data
                    redis_data = await redis_client.get(key)
                    if not redis_data:
                        continue

                    entry_data = json.loads(redis_data)

                    # Handle both single items and lists
                    items_to_process = [entry_data] if isinstance(entry_data, dict) else entry_data

                    for item_data in items_to_process:
                        try:
                            # Skip if no project_id
                            if not item_data.get('project_id'):
                                logger.warning(f"Skipping entry with missing project_id from key {key}")
                                continue

                            # Skip if we've already processed this project_id
                            if item_data['project_id'] in processed_project_ids:
                                continue

                            processed_project_ids.add(item_data['project_id'])

                            # Clean empty values
                            if item_data.get('project_barcode_image_url') == '':
                                item_data['project_barcode_image_url'] = None
                            
                            if item_data.get('material') == '':
                                item_data['material'] = None

                            # Convert to Pydantic model
                            redis_entry = ToEventRedisOut(**item_data)
                            entry_dict = redis_entry.dict(exclude={'created_at', 'updated_at'})

                            # Check for existing record
                            existing = await db.execute(
                                select(ToEventInventory)
                                .where(ToEventInventory.project_id == redis_entry.project_id)
                            )
                            existing = existing.scalar_one_or_none()

                            if existing:
                                # Merge strategy for existing records
                                for field, value in entry_dict.items():
                                    if hasattr(existing, field) and value is not None:
                                        # Preserve newer data
                                        redis_timestamp = redis_entry.updated_at
                                        db_timestamp = getattr(existing, 'updated_at', None)

                                        if (field == 'updated_at' or 
                                            (db_timestamp and redis_timestamp <= db_timestamp)):
                                            continue

                                        setattr(existing, field, value)

                                existing.updated_at = datetime.now(timezone.utc)
                                logger.info(f"Merged existing record: {redis_entry.project_id}")
                            else:
                                # Create new record
                                new_entry = ToEventInventory(**entry_dict)
                                db.add(new_entry)
                                logger.info(f"Created new record: {redis_entry.project_id}")

                            uploaded_entries.append(redis_entry)
                            success_count += 1

                        except Exception as e:
                            error_count += 1
                            logger.error(f"Error processing item {item_data.get('project_id')}: {str(e)}")
                            continue

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing Redis key {key}: {str(e)}")
                    continue
                
            await db.commit()

            # Optional: Clear processed Redis keys
            # if success_count > 0:
            #     await redis_client.delete(*all_keys)

            logger.info(
                f"Upload completed: {success_count} successes, {error_count} errors\n"
                f"Processed keys: {len(inventory_keys)} inventory, {len(project_keys)} projects"
            )
            return uploaded_entries

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error during upload: {e}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        except Exception as e:
            logger.error(f"Unexpected upload error: {e}")
            raise HTTPException(status_code=500, detail="Upload process failed")    

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
                project_barcode_image_url=inventory_data.get('project_barcode_image_url', 'None')
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
            print(f"Searching for {redis_key}")
            redis_data = await redis_client.get(redis_key)
            print(f"Found {redis_data}")

            if redis_data:
                try:
                    redis_items = json.loads(redis_data)
                    if isinstance(redis_items, list):
                        return [ToEventRedisOut.model_validate(item) for item in redis_items]
                    print(f"Found {len(redis_items)} items in Redis")
                    return [ToEventRedisOut.model_validate(json.loads(redis_data))]
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.error(f"Invalid Redis data for {redis_key}: {e}")
                    # Fall through to DB query

            # Fallback to database
            result = await db.execute(
                select(ToEventInventory).where(ToEventInventory.project_id == project_id)
            )
            items = result.scalars().all()
            print(f"Found {len(items)} items in DB")

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
        
    # Update Project in local Redis
    async def update_to_event_project(
        self,
        project_id: str,
        update_data: ToEventRedisUpdate
    ) -> ToEventRedisOut:
        try:
            to_event_inventory = f"to_event_inventory:{project_id}"
            redis_data = await redis_client.get(to_event_inventory)

            if not redis_data:
                raise HTTPException(status_code=404, detail="Item not found in Redis")

            existing_data = json.loads(redis_data)

            # Handle both single item and list cases
            items = [existing_data] if isinstance(existing_data, dict) else existing_data

            if not items:
                raise HTTPException(status_code=404, detail="Project not found")

            # Convert update data to dict
            update_dict = update_data.dict(exclude_unset=True)

            # Find and update matching item
            updated = False
            for item in items:
                if item.get('project_id') == project_id:
                    item.update(update_dict)
                    updated = True
                    break

            if not updated:
                raise HTTPException(status_code=404, detail="Project not found")

            # Save back to Redis
            await redis_client.set(
                to_event_inventory,
                json.dumps(items, default=str)
            )

            return ToEventRedisOut(**items[0])

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid data format in Redis")
        except Exception as e:
            logger.error(f"Error updating item in Redis: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

