# backend/app/crud/wastage_inventory_crud.py
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
from backend.app.schema.wastage_inventory_schema import *
from backend.app.database.redisclient import redis_client
from backend.app import config
from backend.app.utils.barcode_generator import BarcodeGenerator
from typing import Union
from backend.app.interface.wastage_inventory_interface import WastageInventoryInterface

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WastageInventoryService(WastageInventoryInterface):
    def __init__(self, base_url: str = config.BASE_URL, redis_client: redis.Redis = redis_client):
        self.base_url = base_url
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()

    async def upload_wastage_inventory(self, db: AsyncSession) -> List[WastageInventoryRedisOut]:
        """Upload all wastage inventory entries from Redis to database with bulk upsert."""
        try:
            await db.rollback()  # Start fresh
            inventory_keys = await self.redis.keys("wastage_inventory:*")
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
                            if not entry_data.get('id'):
                                logger.warning(f"Entry missing ID in key {key}")
                                continue

                            entry_id = entry_data["id"]
                            if entry_id in processed_ids:
                                logger.debug(f"Skipping duplicate ID {entry_id}")
                                continue
                                
                            processed_ids.add(entry_id)

                            # Clean and validate the data
                            try:
                                validated_data = WastageInventoryRedisIn(**entry_data).model_dump()
                                all_validated_data.append(validated_data)
                                # Keep for response
                                uploaded_entries.append(WastageInventoryRedisOut(**validated_data))
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
                stmt = insert(WastageInventory).values(all_validated_data)
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

        # Create new entry of wastage inventory for to_event which is directly stored in redis
    
    async def create_wastage_inventory(self,  db: AsyncSession, item: Union[WastageInventoryCreate, dict]) -> WastageInventory:
        try:
            if isinstance(item, WastageInventoryCreate):
                wastage_data = item.model_dump(exclude_unset=True)
            else:
                wastage_data = item
                
            if not wastage_data.get('id'):
                wastage_data['id'] = str(uuid.uuid4())
                
            current_time = datetime.now(timezone.utc).replace(tzinfo=None)
            wastage_data['updated_at'] = current_time.isoformat()
            wastage_data['created_at'] = current_time.isoformat()
            
            if not wastage_data.get('employee_name'):
                raise ValueError("employee_name is required")
            if not wastage_data.get('inventory_id'):
                raise ValueError("inventory_id is required")

            # Convert quantity to int if it exists
            if 'quantity' in wastage_data and wastage_data['quantity'] is not None:
                try:
                    wastage_data['quantity'] = int(float(wastage_data['quantity']))
                except (ValueError, TypeError):
                    raise ValueError("Quantity must be a valid number")

            # Generate barcode if not provided
            if not wastage_data.get('wastage_barcode'):
                barcode_data = {
                    'employee_name': wastage_data['employee_name'],
                    'inventory_id': wastage_data['inventory_id'],
                    'id': wastage_data['id']
                }
                barcode, unique_code = self.barcode_generator.generate_linked_codes(barcode_data)
                wastage_data['wastage_barcode'] = barcode
                wastage_data['wastage_barcode_unique_code'] = unique_code
                wastage_data['wastage_barcode_image_url'] = wastage_data.get('wastage_barcode_image_url', "")

            # Store in Redis
            redis_key = f"wastage_inventory:{wastage_data['employee_name']}{wastage_data['inventory_id']}"
            await self.redis.set(redis_key, json.dumps(wastage_data, default=str))
            
            # Return the data in the correct format
            return WastageInventory(**wastage_data)

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:            
            logger.error(f"Failed to create wastage inventory: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create wastage inventory: {str(e)}"
            )

        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:            
            logger.error(f"Failed to create wastage inventory: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create wastage inventory: {str(e)}"
            )
        
    # load submitted wastage inventory 
    async def list_added_wastage_inventory(self, db: AsyncSession, skip: int = 0) -> List[WastageInventoryRedisOut]:
        try:
            # Get all keys matching your project pattern
            keys = await self.redis.keys("wastage_inventory:*")
            
            wastage = []
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        wastage_data = json.loads(data)
                        # Handle the 'cretaed_at' typo if present
                        if 'cretaed_at' in wastage_data and wastage_data['cretaed_at'] is not None:
                            wastage_data['created_at'] = wastage_data['cretaed_at']                            
                        # Validate the data against your schema
                        validated_project = WastageInventoryRedisOut.model_validate(wastage_data)
                        wastage.append(validated_project)
                    except ValidationError as ve:
                        logger.warning(f"Validation error for project {key}: {ve}")
                        continue
            
            # Sort by updated_at (descending)
            wastage.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination
            paginated_wastage = wastage[skip:skip+1000]  # Assuming page size of 1000
            
            return paginated_wastage
        except Exception as e:
            logger.error(f"Redis error fetching entries: {e}")
            raise HTTPException(status_code=500, detail="Redis error")

    # search all wastage inventory from local Redis [project_id, product_id, inventory_id, employee_name] 
    async def search_wastage_by_fields(
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
                "wastage_inventory:*",
                "from_event_inventory:*",
                "inventory:*", 
                "inventory_item:*",
                "to_event_inventory:*",
                "assignment:*",
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
                        if key_str.startswith("wastage_inventory:"):
                            try:
                                validated_data = WastageInventoryRedisOut(**entry)
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
                
    # Update WastageInventory form `employee_name` and `inventory_id` directly from local Redis
    async def update_wastage_inventory(
        self, 
        update_dict: dict
    ) -> WastageInventoryRedisOut:
        try:
            # Format IDs if needed
            inventory_id = update_dict['inventory_id']
            if not inventory_id.startswith('INV'):
                inventory_id = f"INV{inventory_id}"
                
            employee_name = update_dict['employee_name']
            
            # Create Redis key with consistent prefix
            redis_key = f"wastage_inventory:{employee_name}{inventory_id}"
            
            # Get existing record from Redis
            existing_data = await self.redis.get(redis_key)
            if not existing_data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Wastage not found with key: {redis_key}"
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
                'wastage_barcode': existing_dict.get('wastage_barcode'),
                'wastage_barcode_unique_code': existing_dict.get('wastage_barcode_unique_code'),
                'created_at': existing_dict.get('created_at'),
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
            
            return WastageInventoryRedisOut(**updated_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis update failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update wastage inventory: {str(e)}"
            )
        
    #  Show all WastageInventory from local Redis 
    async def show_all_wastage_inventory_from_redis(self, skip: int = 0) -> List[WastageInventoryRedisOut]:
        try:
            # Get all keys matching the pattern
            keys = await self.redis.keys("wastage_inventory:*")
            
            wastage_items = []
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        wastage_data = json.loads(data)
                        
                        # Fix any typos in field names
                        if 'cretaed_at' in wastage_data:
                            wastage_data['created_at'] = wastage_data.pop('cretaed_at')
                        
                        # Convert string datetimes to datetime objects for comparison
                        if 'updated_at' in wastage_data and isinstance(wastage_data['updated_at'], str):
                            try:
                                wastage_data['updated_at'] = datetime.fromisoformat(wastage_data['updated_at'])
                            except ValueError:
                                wastage_data['updated_at'] = datetime.now()
                        
                        # Validate the data
                        validated_item = WastageInventoryRedisOut.model_validate(wastage_data)
                        wastage_items.append(validated_item)
                    except ValidationError as ve:
                        logger.warning(f"Validation error for key {key}: {ve}")
                        continue
            
            # Sort by updated_at (descending) with proper datetime handling
            wastage_items.sort(
                key=lambda x: (
                    x.updated_at.replace(tzinfo=None) 
                    if x.updated_at and x.updated_at.tzinfo 
                    else x.updated_at
                ) if x.updated_at else datetime.min,
                reverse=True
            )
            
            # Apply pagination
            paginated_items = wastage_items[skip : skip + 1000]  # Assuming page size of 1000
            
            return paginated_items
                            
        except Exception as e:            
            logger.error(f"Redis error fetching entries: {e}")
            raise ValueError(f"Error retrieving wastage inventory: {e}")

    # Delete an wastage inventory
    async def delete_wastage_inventory(
        self,
        employee_name: str,
        inventory_id: str
    ) -> WastageInventoryRedisOut:
        try:
            # Format inventory_id if needed
            if not inventory_id.startswith('INV'):
                inventory_id = f"INV{inventory_id}"
            
            # Create the Redis key pattern (match your actual key structure)
            redis_key = f"wastage_inventory:{employee_name}{inventory_id}"
                        
            # Check if the wastage inventory exists
            if not await self.redis.exists(redis_key):
                raise HTTPException(
                    status_code=404,
                    detail=f"Wastage not found for employee {employee_name} and inventory {inventory_id}"
                )
            
            # Get the data before deleting (for returning)
            wastage_data = await self.redis.get(redis_key)
            deleted_item = json.loads(wastage_data) if wastage_data else None
            
            # Delete the specific wastage inventory
            await self.redis.delete(redis_key)
            
            return {
                "status": "success",
                "message": "Wastage deleted successfully",
                "deleted_item": deleted_item
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete wastage inventory: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete wastage inventory: {str(e)}"
            )
        
    # Get the wastage inventory by it's Employee name inventory_id
    async def get_wastage_inventory(
        self, 
        employee_name: str, 
        inventory_id: str
    ) -> WastageInventoryRedisOut:
        try:
            # Create the Redis key pattern
            redis_key = f"wastage_inventory:{employee_name}{inventory_id}"
            
            # Alternative pattern if the key might be different
            # redis_key_pattern = f"wastage_inventory:*{inventory_id}"
            # matching_keys = await self.redis.keys(redis_key_pattern)
            # if matching_keys:
            #     redis_key = matching_keys[0]
            
            # Get data from Redis
            wastage_data = await self.redis.get(redis_key)
            
            if not wastage_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Wastage not found with key: {redis_key}"
                )
            
            # Parse and validate the data
            try:
                data = json.loads(wastage_data)
                # Handle any field name inconsistencies
                if 'cretaed_at' in data:
                    data['created_at'] = data.pop('cretaed_at')
                
                return WastageInventoryRedisOut.model_validate(data)
            except ValidationError as ve:
                logger.error(f"Validation error for key {redis_key}: {ve}")
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid data format in Redis: {str(ve)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching wastage inventory: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching wastage inventory: {str(e)}"
            )
        
    #  Drop Down search list option  ComboBox Widget for wastage inventory directly from redis
    async def wastage_inventory_ComboBox(self, db: AsyncSession, skip: int = 0, keys: str = None) -> List[WastageInventoryRedisOut]:
        try:
            # Get all keys matching your project pattern
            keys = await self.redis.keys(
            # Determine key patterns to search
            key_patterns = [keys] if keys else [
                "wastage_inventory:*",
                "from_event_inventory:*",
                "inventory:*", 
                "inventory_item:*",
                "to_event_inventory:*",
                "assignment:*",
            ])

            
            wastage_items = []
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        wastage_data = json.loads(data)
                        # Handle the 'cretaed_at' typo if present
                        if 'cretaed_at' in wastage_data and wastage_data['cretaed_at'] is not None:
                            wastage_data['created_at'] = wastage_data.pop('cretaed_at')
                        
                        # Validate the data
                        validated_item = WastageInventoryRedisOut.model_validate(wastage_data)
                        wastage_items.append(validated_item)
                    except ValidationError as ve:
                        logger.warning(f"Validation error for key {key}: {ve}")
                        continue
            
            # Sort by updated_at (descending) with proper datetime handling
            wastage_items.sort(
                key=lambda x: (
                    x.updated_at.replace(tzinfo=None) 
                    if x.updated_at and x.updated_at.tzinfo 
                    else x.updated_at
                ) if x.updated_at else datetime.min,
                reverse=True
            )
            
            # Apply pagination
            paginated_items = wastage_items[skip : skip + 1000]  # Assuming page size of 1000
            
            return paginated_items
                            
        except Exception as e:            
            logger.error(f"Redis error fetching entries: {e}")            
            raise ValueError(f"Error retrieving wastage inventory: {e}")