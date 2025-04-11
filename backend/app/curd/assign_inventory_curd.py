# backend/app/crud/assign_inventory_crud.py
from datetime import datetime, timezone, date
from typing import List, Optional
import json
import logging
import uuid
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update

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
    RedisSearchResult
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
        """Upload all assign_inventory entries from Redis to database with bulk upsert."""
        try:
            await db.rollback()  # Start fresh
            inventory_keys = await self.redis.keys("assignment:*")
            uploaded_entries = []
            processed_ids = set()
            all_validated_data = []

            # First pass: validate all data and collect for bulk operation
            for key in inventory_keys:
                try:
                    redis_data = await self.redis.get(key)
                    if not redis_data:
                        continue

                    try:
                        data = json.loads(redis_data)
                        if isinstance(data, dict):
                            data = [data]  # Normalize to list
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON for key {key}")
                        continue

                    for entry_data in data:
                        try:
                            if not entry_data.get("id"):
                                logger.warning(f"Entry missing ID in key {key}")
                                continue

                            entry_id = entry_data["id"]
                            if entry_id in processed_ids:
                                logger.debug(f"Skipping duplicate ID {entry_id}")
                                continue
                                
                            processed_ids.add(entry_id)

                            # Clean and validate the data
                            try:
                                validated_data = AssignmentInventoryRedisIn(**entry_data).model_dump()
                                all_validated_data.append(validated_data)
                                # Keep for response
                                uploaded_entries.append(AssignmentInventoryRedisOut(**validated_data))
                            except ValidationError as ve:
                                logger.error(f"Validation error for entry {entry_id}: {ve}")
                                continue

                        except Exception as e:
                            logger.error(f"Error processing entry {entry_id}: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Error processing key {key}: {e}")
                    continue

            if not all_validated_data:
                raise HTTPException(status_code=404, detail="No valid inventory items found in Redis")

            # Bulk upsert operation
            try:
                stmt = insert(AssignmentInventory).values(all_validated_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],
                    set_={k: v for k, v in stmt.excluded.items() if k != 'id'}
                )
                await db.execute(stmt)
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(f"Bulk upsert failed: {e}")
                raise

            return uploaded_entries

        except Exception as e:
            await db.rollback()
            logger.error(f"Upload operation failed: {e}", exc_info=True)
            raise

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
                        assigned_data = json.loads(data)
                        # Handle the 'cretaed_at' typo if present
                        if 'cretaed_at' in assigned_data and 'created_at' not in assigned_data:
                            assigned_data['created_at'] = assigned_data['cretaed_at']
                        # Validate the data against your schema
                        validated_project = AssignmentInventoryRedisOut.model_validate(assigned_data)
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
        employee_name: Optional[str] = None,
        key_pattern: Optional[str] = None
    ) -> List[RedisSearchResult]:
        try:
            def format_id(value: Optional[str], prefix: str) -> Optional[str]:
                if not value:
                    return None
                value = str(value).strip()
                if not value.startswith(prefix):
                    return f"{prefix}{value}"
                return value

            # Format IDs
            formatted_inventory_id = format_id(inventory_id, "INV")
            formatted_project_id = format_id(project_id, "PRJ") 
            formatted_product_id = format_id(product_id, "PRD")

            # Build search filters
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

            # Determine key patterns to search
            key_patterns = [key_pattern] if key_pattern else [
                "assignment:*",
                "from_event_inventory:*",
                "inventory:*", 
                "inventory_item:*",
                "to_event_inventory:*"
            ]

            # Scan Redis
            results = []
            for pattern in key_patterns:
                async for key in self.redis.scan_iter(match=pattern):
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                    
                    data = await self.redis.get(key_str)
                    if not data:
                        continue

                    try:
                        entry = json.loads(data)
                        
                        # Apply filters
                        if not all(f(entry) for f in search_filters):
                            continue
                        
                        # Create proper RedisSearchResult object
                        if key_str.startswith("assignment:"):
                            try:
                                validated_data = AssignmentInventoryRedisOut(**entry)
                                results.append(RedisSearchResult(
                                    key=key_str,
                                    data=validated_data
                                ))
                            except ValidationError:
                                results.append(RedisSearchResult(
                                    key=key_str,
                                    data=entry
                                ))
                        else:
                            results.append(RedisSearchResult(
                                key=key_str,
                                data=entry
                            ))
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
                detail=f"Failed to search Redis data: {str(e)}"
            )
                
    # Update Assignment Inventory form `employee_name` and `inventory_id` directly from local Redis
    async def update_assignment_inventory(
        self, 
        update_dict: dict
    ) -> AssignmentInventoryRedisOut:
        try:
            # Format IDs if needed
            inventory_id = update_dict['inventory_id']
            if not inventory_id.startswith('INV'):
                inventory_id = f"INV{inventory_id}"
                
            employee_name = update_dict['employee_name']
            
            # Create Redis key with consistent prefix
            redis_key = f"assignment:{employee_name}{inventory_id}"
            
            # Get existing record from Redis
            existing_data = await self.redis.get(redis_key)
            if not existing_data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Assignment not found with key: {redis_key}"
                )
            
            # Parse existing record
            existing_dict = json.loads(existing_data)
            
            # Verify immutable fields haven't changed
            immutable_fields = {
                'id': existing_dict.get('id'),
                'inventory_id': existing_dict.get('inventory_id'),
                'project_id': existing_dict.get('project_id'),
                'product_id': existing_dict.get('product_id'),
                'employee_name': existing_dict.get('employee_name'),
                'assignment_barcode': existing_dict.get('assignment_barcode'),
                'assignment_barcode_unique_code': existing_dict.get('assignment_barcode_unique_code'),
                'created_at': existing_dict.get('created_at'),
                'assign_by': existing_dict.get('assign_by'),
                'assigned_date': existing_dict.get('assigned_date')
            }
            
            # Update only allowed fields (remove the path parameters)
            update_dict.pop('employee_name', None)
            update_dict.pop('inventory_id', None)
            
            # Merge updates while preserving immutable fields
            updated_dict = {**existing_dict, **update_dict, **immutable_fields}
            updated_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Convert all datetime objects to ISO format strings
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, date):
                    return obj.isoformat()
                return obj
            
            # Apply conversion to all values in the dictionary
            serializable_dict = {k: convert_datetime(v) for k, v in updated_dict.items()}
            
            # Save back to Redis
            await self.redis.set(redis_key, json.dumps(serializable_dict))
            
            return AssignmentInventoryRedisOut(**updated_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis update failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update assignment: {str(e)}"
            )
        
    #  Show all Assigned Inventory from local Redis 
    async def show_all_assigned_inventory_from_redis(self, skip: int = 0) -> List[AssignmentInventoryRedisOut]:
        try:
            # Get all keys matching your project pattern
            keys = await self.redis.keys("assignment:*")
            
            projects = []
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        assigned_data = json.loads(data)
                        # Handle the 'cretaed_at' typo if present
                        if 'cretaed_at' in assigned_data and assigned_data['cretaed_at'] is not None:
                            assigned_data['created_at'] = assigned_data['cretaed_at']
                        # Validate the data against your schema
                        validated_project = AssignmentInventoryRedisOut.model_validate(assigned_data)
                        projects.append(validated_project)
                    except ValidationError as ve:
                        logger.warning(f"Validation error for project {key}: {ve}")
                        continue
            
            # Sort by updated_at (descending)
            projects.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination
            paginated_projects = projects[skip:skip+250]  # Assuming page size of 100
            
            return paginated_projects
        except Exception as e:
            logger.error(f"Redis error fetching entries: {e}")

    # Delete an single assign item by employee_name and inventory_id
    async def delete_assignment(
        self,
        employee_name: str,
        inventory_id: str
    ) -> None:
        try:
            # Format inventory_id if needed
            if not inventory_id.startswith('INV'):
                inventory_id = f"INV{inventory_id}"
            
            # Create the Redis key pattern
            redis_key = f"assignment:{employee_name}{inventory_id}"
            
            # Check if the assignment exists
            if not await self.redis.exists(redis_key):
                raise HTTPException(
                    status_code=404,
                    detail=f"Assignment not found for employee {employee_name} and inventory {inventory_id}"
                )
            
            # Delete the specific assignment
            await self.redis.delete(redis_key)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete assignment: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete assignment: {str(e)}"
            )