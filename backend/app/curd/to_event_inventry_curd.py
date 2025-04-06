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
    ToEventUploadResponse,
    ToEventUploadSchema,
    RedisInventoryItem,
    ToEventRedis,
    ToEventRedisOut,
)
from sqlalchemy.exc import SQLAlchemyError
from backend.app.models.to_event_inventry_model import InventoryItem, ToEventInventory
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
from sqlalchemy import select, delete
from backend.app.utils.barcode_generator import BarcodeGenerator  # Import the BarcodeGenerator class


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

class ToEventInventoryService(ToEventInventoryInterface):
    def __init__(self, base_url: str = config.BASE_URL, redis_client = redis_client):
        self.base_url = base_url
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()

# upload all to_event_inventory entries from local Redis to the database after click on upload data button
    async def upload_to_event_inventory(self, db: AsyncSession) -> List[ToEventUploadResponse]:
        try:
            # Start with fresh transaction
            await db.rollback()
            
            # Get both types of Redis keys
            inventory_keys = await redis_client.keys("to_event_inventory:*")
            item_keys = await redis_client.keys("inventory_item:*")
            
            logger.info(f"Starting upload with {len(inventory_keys)} inventory keys and {len(item_keys)} item keys")
            
            if not inventory_keys and not item_keys:
                logger.info("No Redis keys found to upload")
                return []

            uploaded_entries = []
            success_count = 0
            error_count = 0
            processed_projects = set()

            # Process main inventory entries
            for key in inventory_keys:
                try:
                    # Ensure fresh transaction for each key
                    await db.rollback()
                    
                    redis_data = await redis_client.get(key)
                    if not redis_data:
                        logger.debug(f"Empty data for key {key}")
                        continue

                    try:
                        data = json.loads(redis_data)
                        entries = [ToEventUploadSchema(**item) for item in data] if isinstance(data, list) else [ToEventUploadSchema(**data)]
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Schema validation failed for {key}: {str(e)}")
                        await db.rollback()
                        continue

                    for entry in entries:
                        try:
                            if not entry.project_id:
                                logger.warning(f"Empty project_id in entry from key {key}")
                                continue
                            
                            # Skip if we've already processed this project
                            if entry.project_id in processed_projects:
                                logger.debug(f"Skipping already processed project {entry.project_id}")
                                continue
                                
                            processed_projects.add(entry.project_id)
                            logger.info(f"Processing project {entry.project_id}")

                            # Check if exists in the database
                            existing = await db.execute(
                                select(ToEventInventory)
                                .where(ToEventInventory.project_id == entry.project_id)
                            )
                            existing = existing.scalar_one_or_none()

                            entry_dict = entry.model_dump(exclude={'inventory_items'})

                            if existing:
                                # If the project already exists, delete the old entry
                                await db.execute(
                                    delete(ToEventInventory).where(ToEventInventory.project_id == entry.project_id)
                                )
                                logger.info(f"Deleted existing project with project_id: {entry.project_id}")
                                
                            # Create new entry (whether it existed or not)
                            new_entry = ToEventInventory(**entry_dict)
                            db.add(new_entry)
                            await db.flush()
                            parent_id = new_entry.id

                            # Process inventory items from main entry
                            if entry.inventory_items:
                                for item in entry.inventory_items:
                                    # Check if item already exists
                                    existing_item = await db.execute(
                                        select(InventoryItem)
                                        .where(InventoryItem.id == item.id)
                                    )
                                    existing_item = existing_item.scalar_one_or_none()

                                    item_data = item.model_dump(exclude={'project_id'})

                                    if existing_item:
                                        # Update existing item if necessary
                                        for field, value in item_data.items():
                                            if hasattr(existing_item, field) and getattr(existing_item, field) != value:
                                                setattr(existing_item, field, value)
                                    else:
                                        # Add new item
                                        new_item = InventoryItem(
                                            project_id=parent_id,
                                            **item_data
                                        )
                                        db.add(new_item)

                            # Commit after each successful project
                            await db.commit()
                            
                            # Prepare success response
                            response = ToEventUploadResponse(
                                success=True,
                                message="Copied to database successfully",
                                project_id=entry.project_id,
                                inventory_items_count=len(entry.inventory_items),
                                created_at=entry.created_at or datetime.now(timezone.utc)
                            )
                            uploaded_entries.append(response)
                            success_count += 1
                            logger.info(f"Successfully processed project {entry.project_id}")

                        except Exception as e:
                            await db.rollback()
                            error_count += 1
                            logger.error(f"Error processing entry {entry.project_id if entry else 'unknown'}: {str(e)}")
                            continue

                except Exception as e:
                    await db.rollback()
                    error_count += 1
                    logger.error(f"Error processing key {key}: {str(e)}")
                    continue

            # Process individual inventory items
            for key in item_keys:
                try:
                    # Fresh transaction for each item
                    await db.rollback()
                    
                    redis_data = await redis_client.get(key)
                    if not redis_data:
                        continue

                    try:
                        item_data = json.loads(redis_data)
                        item = RedisInventoryItem(**item_data)
                    except Exception as e:
                        logger.error(f"Schema validation failed for {key}: {str(e)}")
                        error_count += 1
                        continue

                    if not item.project_id:
                        continue

                    # Find the parent project in the database
                    parent = await db.execute(
                        select(ToEventInventory)
                        .where(ToEventInventory.project_id == item.project_id)
                    )
                    parent = parent.scalar_one_or_none()

                    if not parent:
                        logger.warning(f"No parent project found for item {item.id}")
                        continue

                    # Check if item already exists
                    existing_item = await db.execute(
                        select(InventoryItem)
                        .where(InventoryItem.id == item.id)
                    )
                    existing_item = existing_item.scalar_one_or_none()

                    item_data = item.model_dump(exclude={'project_id'})

                    if existing_item:
                        # Update existing item
                        for field, value in item_data.items():
                            if hasattr(existing_item, field) and getattr(existing_item, field) != value:
                                setattr(existing_item, field, value)
                    else:
                        # Add new item
                        new_item = InventoryItem(
                            project_id=parent.id,
                            **item_data
                        )
                        db.add(new_item)
                    
                    # Commit after each item
                    await db.commit()

                    # Update count in response if project was already processed
                    for entry in uploaded_entries:
                        if entry.project_id == item.project_id:
                            entry.inventory_items_count += 1
                            break
                    else:
                        # If project wasn't processed yet, create a new response entry
                        response = ToEventUploadResponse(
                            success=True,
                            message="Copied item to database",
                            project_id=item.project_id,
                            inventory_items_count=1,
                            created_at=datetime.now(timezone.utc)
                        )
                        uploaded_entries.append(response)

                    success_count += 1

                except Exception as e:
                    await db.rollback()
                    error_count += 1
                    logger.error(f"Error processing item {item.id if hasattr(item, 'id') else 'unknown'}: {str(e)}")
                    continue

            logger.info(f"Copy completed: {success_count} items processed, {error_count} errors")
            return uploaded_entries

        except Exception as e:
            await db.rollback()
            logger.error(f"Copy operation failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))    

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
    async def load_submitted_project_from_redis(self, skip: int = 0) -> List[ToEventRedisOut]:
        try:
            # Get all keys matching your project pattern
            keys = await self.redis.keys("to_event_inventory:*")
            
            projects = []
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        project_data = json.loads(data)
                        # Handle the 'cretaed_at' typo if present
                        if 'cretaed_at' in project_data and 'created_at' not in project_data:
                            project_data['created_at'] = project_data['cretaed_at']
                        # Validate the data against your schema
                        validated_project = ToEventRedisOut.model_validate(project_data)
                        projects.append(validated_project)
                    except ValidationError as ve:
                        logger.warning(f"Validation error for project {key}: {ve}")
                        continue
            
            # Sort by updated_at (descending)
            projects.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination
            paginated_projects = projects[skip:skip+10]  # Assuming page size of 10
            
            return paginated_projects
        except Exception as e:
            logger.error(f"Redis error fetching entries: {e}")
            raise HTTPException(status_code=500, detail="Redis error")
    

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

