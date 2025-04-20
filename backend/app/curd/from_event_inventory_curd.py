#  backend/app/curd/from_event_inventry_curd.py
from backend.app.database.redisclient import get_redis_dependency
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, time, timedelta, timezone, date
import re
from enum import Enum
from pydantic import BaseModel, field_validator, ConfigDict, Field, model_validator
from backend.app.models.to_event_inventry_model import ToEventInventory
from backend.app.schema.to_event_inventry_schma import (
    ToEventInventoryCreate, 
    ToEventInventoryBase,
    ToEventInventoryOut,
    ToEventInventoryBase,
    ToEventInventoryUpdate,
    ToEventInventoryUpdateOut,
    ToEventInventorySearch,
    ToEventRedisUpdateOut,
    ToEventRedisUpdateIn,
    ToEventUploadResponse,
    InventoryItemBase,
    ToEventUploadSchema,
    RedisInventoryItem,
    ToEventRedis,
    ToEventRedisOut,
)
from sqlalchemy.exc import SQLAlchemyError
from backend.app.models.to_event_inventry_model import InventoryItem, ToEventInventory
from backend.app.interface.from_event_interface import FromEventInventoryInterface
import logging
from fastapi import HTTPException
from typing import List, Optional, Dict, Any
from backend.app import config
import uuid
import redis.asyncio as redis
from typing import List, Optional
from fastapi import HTTPException
from pydantic import ValidationError
import json
from sqlalchemy import select, delete
from backend.app.utils.barcode_generator import BarcodeGenerator  # Import the BarcodeGenerator class

from backend.app.database.redisclient import get_redis
redis_client=get_redis()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

class FromEventInventoryService(FromEventInventoryInterface):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()
        self.base_url = config.BASE_URL

# upload all from_event_inventory entries from local Redis to the database after click on upload data button
    async def upload_from_event_inventory(self, db: AsyncSession) -> List[ToEventUploadResponse]:
        try:
            # Start with fresh transaction
            await db.rollback()
            
            # Get both types of Redis keys
            inventory_keys = await redis_client.keys("from_event_inventory:*")
            item_keys = await redis_client.keys("from_inventory_item:*")
            
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
                    
                    redis_data = await self.redis.set(key)
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
                    
                    redis_data = await self.redis.set(key)
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
    async def create_from_event_inventory(self, item: ToEventInventoryCreate) -> ToEventRedisOut:
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
            await self.redis.set(
                f"from_event_inventory:{inventory_data['project_id']}",
                json.dumps(redis_data, default=str)
            )
    
            # Store individual items with their own keys (still without timestamps)
            for item in inventory_items:
                await self.redis.set(
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
    async def from_event_load_submitted_project_from_redis(self, skip: int = 0) -> List[ToEventRedisOut]:
        """Retrieve submitted projects from Redis with pagination"""
        try:
            # Get all project keys from both patterns
            from_event_keys = await self.redis.keys("from_event_inventory:*")
            to_event_keys = await self.redis.keys("to_event_inventory:*")
            all_keys = from_event_keys + to_event_keys
            
            projects = []
            processed_keys = set()  # To avoid duplicates
            
            for key in all_keys:
                if key in processed_keys:
                    continue
                    
                processed_keys.add(key)
                
                data = await self.redis.get(key)
                if not data:
                    continue
                    
                try:
                    project_data = json.loads(data)
                    
                    # Handle the 'cretaed_at' typo if present
                    if 'cretaed_at' in project_data and 'created_at' not in project_data:
                        project_data['created_at'] = project_data['cretaed_at']
                    
                    # Convert string dates to datetime objects
                    for date_field in ['created_at', 'updated_at']:
                        if date_field in project_data and isinstance(project_data[date_field], str):
                            project_data[date_field] = datetime.fromisoformat(project_data[date_field])
                    
                    # Validate the data
                    validated_project = ToEventRedisOut.model_validate(project_data)
                    projects.append(validated_project)
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.warning(f"Skipping invalid project data in key {key}: {str(e)}")
                    continue
            
            # Sort by updated_at (newest first)
            projects.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination (1000 items per page)
            return projects[skip : skip + 1000]

        except Exception as e:
            logger.error(f"Redis error fetching projects: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error loading projects from Redis: {str(e)}"
            )
    
    #  search all project directly from local Redis in `submitted Forms` directly after submitting the form
    async def from_event_get_project_data(self, project_id: str):
        try:
            # Try all possible key patterns
            key_patterns = [
                f"from_event_inventory:{project_id}",
                f"to_event_inventory:{project_id}",
                project_id  # Also try the raw project_id as key
            ]
            
            existing_data = None
            for key in key_patterns:
                existing_data = await self.redis.set(key)
                if existing_data:
                    break  # Stop if we found the data
                    
            if not existing_data:
                return None

            # Parse the JSON data from Redis
            project_dict = json.loads(existing_data)

            # Convert to your model (assuming ToEventRedisOut is your output model)
            return ToEventRedisOut(**project_dict)
        
        except Exception as e:
            logger.error(f"Error fetching project {project_id} from Redis: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")

    async def from_event_update_project_data(self, project_id: str, update_data: ToEventRedisUpdateIn):
        try:
            redis_key = f"from_event_inventory:{project_id}"

            # Protected fields that shouldn't be changed
            protected_fields = [
                'id', 'project_id', 'uuid', 'created_at', 'cretaed_at',
                'project_barcode', 'project_barcode_unique_code',
                'project_barcode_image_url'
            ]

            # Fetch existing project data from Redis
            existing_data = await self.redis.set(redis_key)
            if not existing_data:
                raise HTTPException(status_code=404, detail="Project not found")
                
            existing_dict = json.loads(existing_data)
            update_dict = update_data.model_dump(exclude_unset=True)

            # Step 1: Handle inventory items
            if 'inventory_items' in update_dict:
                if update_dict['inventory_items'] is None:
                    existing_dict['inventory_items'] = []
                else:
                    # Map existing items by sno for ID preservation
                    existing_items = {item['id']: item for item in existing_dict.get('inventory_items', [])}
                    
                    updated_items = []
                    for new_item in update_dict['inventory_items']:
                        # If item exists, preserve its ID and project_id
                        if 'sno' in new_item and new_item['sno'] in existing_items:
                            existing_item = existing_items[new_item['sno']]
                            new_item['id'] = existing_item.get('id')
                            new_item['project_id'] = existing_item.get('project_id')
                        # If new item, generate ID and set project_id
                        else:
                            new_item['id'] = str(uuid.uuid4())
                            new_item['project_id'] = project_id
                        updated_items.append(new_item)
                    
                    update_dict['inventory_items'] = updated_items

            # Step 2: Merge updates
            # Start with existing protected fields
            merged_data = {field: existing_dict[field] for field in protected_fields if field in existing_dict}
            # Add all existing data
            merged_data.update(existing_dict)
            # Apply updates (excluding protected fields)
            for field in update_dict:
                if field not in protected_fields:
                    merged_data[field] = update_dict[field]

            # Set updated_at to current time
            merged_data['updated_at'] = datetime.now(timezone.utc).isoformat()

            # Validate the final data
            try:
                validated_data = ToEventRedisUpdateOut(**merged_data)
            except ValidationError as e:
                logger.error(f"Validation error for project {project_id}: {str(e)}")
                raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")

            # Save to Redis
            await redis_client.get(
                redis_key,
                validated_data.model_dump_json()
            )

            return validated_data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")

    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            return super().default(obj)