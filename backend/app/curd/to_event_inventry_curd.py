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

                            # Generate UUID if id is missing
                            if 'id' not in item_data:
                                item_data['id'] = str(uuid.uuid4())

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
    async def create_to_event_inventory(self, item: ToEventInventoryCreate) -> ToEventRedisOut:
        try:
            """Create inventory with multiple items directly in Redis"""
            # Convert to dict and clean data
            inventory_data = item.model_dump(exclude_unset=True)
    
            # Generate UUID and timestamps
            current_time = datetime.now(timezone.utc)
            inventory_id = str(uuid.uuid4())
    
            # Set common fields for the project
            inventory_data.update({
                'id': inventory_id,
                'uuid': inventory_id,
                'created_at': current_time,  # Timestamp only in main record
                'updated_at': current_time   # Timestamp only in main record
            })
    
            # Generate barcodes if not provided
            if not inventory_data.get('project_barcode'):
                barcode, unique_code = self.barcode_generator.generate_linked_codes(inventory_data)
                inventory_data.update({
                    'project_barcode': barcode,
                    'project_barcode_unique_code': unique_code
                })
    
                # Set an empty image URL if not provided
                if not inventory_data.get('project_barcode_image_url'):
                    inventory_data['project_barcode_image_url'] = ""
    
            # Process multiple inventory items (without timestamps)
            inventory_items = []
            for item_data in inventory_data.get('inventory_items', []):
                item_id = str(uuid.uuid4())
                inventory_items.append({
                    **item_data,
                    'id': item_id,
                    'project_id': inventory_data['project_id']  # Only include project_id
                    # Removed created_at and updated_at from items
                })
    
            # Prepare complete Redis data structure
            redis_data = {
                **inventory_data,
                'inventory_items': inventory_items
            }
    
            # Store main inventory in Redis
            await redis_client.set(
                f"to_event_inventory:{inventory_data['project_id']}",
                json.dumps(redis_data, default=str)
            )
    
            # Store individual items with their own keys (still without timestamps)
            for item in inventory_items:
                await redis_client.set(
                    f"inventory_item:{item['id']}",
                    json.dumps(item, default=str)
                )
    
            return ToEventRedisOut(**redis_data)
    
        except Exception as e:
            logger.error(f"Redis storage failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create inventory: {str(e)}"
            )
    
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

    async def search_entries_by_project_id(self, db: AsyncSession, search_filter: ToEventInventorySearch):
        try:
            project_id = search_filter.project_id
            redis_key = f"to_event_inventory:{project_id}"
            redis_data = await redis_client.get(redis_key)

            if redis_data:
                data = json.loads(redis_data)
                # Convert to list of items with project info
                items = []
                for item in data['inventory_items']:
                    combined = {**data['project_info'], **item}
                    items.append(ToEventRedisOut(**combined))
                return items

            # Fallback to database
            result = await db.execute(
                select(ToEventInventory).where(ToEventInventory.project_id == project_id)
            )
            items = result.scalars().all()
            return [ToEventRedisOut.model_validate(item) for item in items]

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
    async def update_to_event_project(self, project_id: str, update_data: ToEventRedisUpdate):
        try:
            redis_key = f"to_event_inventory:{project_id}"
            redis_data = await redis_client.get(redis_key)
    
            if not redis_data:
                raise HTTPException(status_code=404, detail="Project not found")
    
            data = json.loads(redis_data)
            
            # Update project info
            if update_data.project_info:
                data['project_info'].update(update_data.project_info.dict(exclude_unset=True))
                data['project_info']['updated_at'] = datetime.now(timezone.utc).isoformat()
    
            # Update specific items if provided
            if update_data.inventory_items:
                for updated_item in update_data.inventory_items:
                    for i, item in enumerate(data['inventory_items']):
                        if item.get('sno') == updated_item.sno:
                            data['inventory_items'][i].update(updated_item.dict(exclude_unset=True))
                            break
                        
            await redis_client.set(redis_key, json.dumps(data, default=str))
            return ToEventRedisOut(**data['project_info'])
    
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

