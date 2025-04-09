# backend/app/crud/assign_inventory_crud.py
from datetime import datetime, timezone
from typing import List, Optional
import json
import logging
import uuid

from fastapi import HTTPException, Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import redis.asyncio as redis

from backend.app.interface.assign_inventory_interface import AssignmentInventoryInterface
from backend.app.models.assign_inventory_model import AssignmentInventory
from backend.app.schema.assign_inventory_schema import (
    AssignmentInventoryCreate,
    AssignmentInventoryOut,
    AssignmentInventoryUpdate,
    AssignmentInventoryRedisIn,
    AssignmentInventoryRedisOut,
    AssignmentInventorySearch,
)
from backend.app.database.redisclient import redis_client
from backend.app import config
from backend.app.utils.barcode_generator import BarcodeGenerator
from typing import Union

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AssignInventoryService(AssignmentInventoryInterface):
    def __init__(self, base_url: str = config.BASE_URL, redis_client: redis.Redis = redis_client):
        self.base_url = base_url
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()

    async def upload_from_event_inventory(self, db: AsyncSession) -> List[AssignmentInventoryRedisOut]:
        """Upload all assign_inventory entries from Redis to database."""
        try:
            await db.rollback()  # Start fresh
            inventory_keys = await self.redis.keys("assignment:*")
            uploaded_entries = []
            processed_projects = set()

            for key in inventory_keys:
                try:
                    redis_data = await self.redis.get(key)
                    if not redis_data:
                        logger.debug(f"Empty data for key {key}")
                        continue

                    try:
                        data = json.loads(redis_data)
                        entries = (
                            [AssignmentInventoryRedisIn(**item) for item in data] 
                            if isinstance(data, list) 
                            else [AssignmentInventoryRedisIn(**data)]
                        )
                    except ValidationError as ve:
                        logger.error(f"Validation error for key {key}: {ve}")
                        continue

                    for entry in entries:
                        try:
                            if not entry.project_id:
                                logger.warning(f"Empty project_id in entry from key {key}")
                                continue
                            
                            if entry.project_id in processed_projects:
                                logger.debug(f"Skipping duplicate project {entry.project_id}")
                                continue
                                
                            processed_projects.add(entry.project_id)

                            # Check for existing entry
                            existing = await db.execute(
                                select(AssignmentInventory)
                                .where(AssignmentInventory.project_id == entry.project_id)
                            )
                            existing = existing.scalar_one_or_none()

                            if existing:
                                await db.delete(existing)
                                logger.info(f"Removed existing project {entry.project_id}")

                            # Create new entry
                            new_entry = AssignmentInventory(**entry.model_dump())
                            db.add(new_entry)
                            await db.commit()

                            uploaded_entries.append(
                                AssignmentInventoryRedisOut(
                                    **entry.model_dump(),
                                    success=True,
                                    message="Uploaded successfully"
                                )
                            )
                            logger.info(f"Processed project {entry.project_id}")

                        except Exception as e:
                            await db.rollback()
                            logger.error(f"Error processing entry {entry.project_id}: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Error processing key {key}: {e}")
                    continue

            return uploaded_entries

        except Exception as e:
            await db.rollback()
            logger.error(f"Upload operation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload inventory data: {str(e)}"
            ) 
        
# Create new entry of inventory for to_event which is directly stored in redis
    async def create_assignment_inventory(self, db: AsyncSession, item: Union[AssignmentInventoryCreate, dict]) -> AssignmentInventory:
        try:
            if isinstance(item, AssignmentInventoryCreate):
                inventory_data = item.model_dump(exclude_unset=True)
            else:
                inventory_data = item
                
            if not inventory_data.get('id'):
                inventory_data['id'] = str(uuid.uuid4())
                
            current_time = datetime.now(timezone.utc)
            inventory_data['updated_at'] = current_time
            inventory_data['created_at'] = current_time 
            
            if not inventory_data.get('employee_name'):
                raise ValueError("employee_name is required")
            if not inventory_data.get('inventory_id'):
                raise ValueError("inventory_id is required")

            if not inventory_data.get('assignment_barcode'):
                barcode_data = {
                    'employee_name': inventory_data['employee_name'],
                    'inventory_id': inventory_data['inventory_id'],
                    'id': inventory_data['id']
                }
                barcode, unique_code = self.barcode_generator.generate_linked_codes(barcode_data)
                inventory_data.update({
                    'assignment_barcode': barcode,
                    'assignment_barcode_unique_code': unique_code,
                    'assignment_barcode_image_url': inventory_data.get('assignment_barcode_image_url', "")
                })

            redis_key = f"assignment:{inventory_data['employee_name']}{inventory_data['inventory_id']}"            
            await self.redis.set(redis_key, json.dumps(inventory_data, default=str))
            return AssignmentInventory(**inventory_data)

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"Redis storage failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create assignment inventory: {str(e)}"
            )
        
    # load submitted assigned inventory 
    async def list_added_assigned_inventory(self, db: AsyncSession, skip: int = 0) -> List[AssignmentInventoryRedisOut]:
        try:
            # Get all keys matching your project pattern
            keys = await self.redis.keys("assignment:*")
            
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
                        validated_project = AssignmentInventoryRedisOut.model_validate(project_data)
                        projects.append(validated_project)
                    except ValidationError as ve:
                        logger.warning(f"Validation error for project {key}: {ve}")
                        continue
            
            # Sort by updated_at (descending)
            projects.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination
            paginated_projects = projects[skip:skip+500]  # Assuming page size of 100
            
            return paginated_projects
        except Exception as e:
            logger.error(f"Redis error fetching entries: {e}")
            raise HTTPException(status_code=500, detail="Redis error")

    # search all assigned inventory from local Redis [project_id, product_id, inventory_id, employee_name] 
    async def search_entries_by_fields(
        self,
        db: AsyncSession,
        inventory_id: Optional[str] = None,
        project_id: Optional[str] = None,
        product_id: Optional[str] = None,
        employee_name: Optional[str] = None
    ) -> List[AssignmentInventoryRedisOut]:
        try:
            def format_id(value: Optional[str], prefix: str) -> Optional[str]:
                if not value:
                    return None
                value = str(value).strip()
                if not value.startswith(prefix):
                    return f"{prefix}{value}"
                return value

            # Format IDs if they're provided (accepts both with and without prefixes)
            formatted_inventory_id = format_id(inventory_id, "INV")
            formatted_project_id = format_id(project_id, "PRJ") 
            formatted_product_id = format_id(product_id, "PRD")

            # First check if we're searching by employee_name and inventory_id (direct key lookup)
            if employee_name and formatted_inventory_id:
                redis_key = f"{employee_name}{formatted_inventory_id}"
                data = await self.redis.get(redis_key)
                if data:
                    entry = json.loads(data)
                    return [AssignmentInventoryRedisOut(**entry)]
            
            # Build search filters using formatted IDs
            search_filters = []
            if employee_name:
                search_filters.append(lambda x: x.get('employee_name') == employee_name)
            if formatted_inventory_id:
                search_filters.append(lambda x: x.get('inventory_id') == formatted_inventory_id)
            if formatted_project_id:
                search_filters.append(lambda x: x.get('project_id') == formatted_project_id)
            if formatted_product_id:
                search_filters.append(lambda x: x.get('product_id') == formatted_product_id)
            
            if not search_filters:
                raise ValueError("At least one search parameter must be provided")
            
            # Scan Redis for matching entries
            results = []
            async for key in self.redis.scan_iter(match="*"):
                # Convert key to string if it's bytes
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                
                # Skip if key doesn't look like an assignment key
                if not (":" in key_str and key_str.startswith("assignment:")):
                    continue
                    
                data = await self.redis.get(key_str)
                if data:
                    try:
                        entry = json.loads(data)
                        if all(f(entry) for f in search_filters):
                            results.append(AssignmentInventoryRedisOut(**entry))
                    except json.JSONDecodeError:
                        continue
            
            return results
        
        except ValueError as ve:
            logger.error(f"Validation error in search: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"Redis search failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to search assignment inventory: {str(e)}"
            )