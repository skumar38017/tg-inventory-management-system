# backend/app/crud/assign_inventory_crud.py
from backend.app.utils.common_imports import *

from backend.app.interface.assign_inventory_interface import AssignmentInventoryInterface
from backend.app.models.assign_inventory_model import AssignmentInventory
from backend.app.schema.assign_inventory_schema import (
    AssignmentInventoryCreate,
    AssignmentInventoryRedisOut,
    RedisSearchResult
)

import logging

logger = logging.getLogger(__name__)

class AssignInventoryService(AssignmentInventoryInterface):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.InventoryUpdater = InventoryUpdater(redis_client)
        self.barcode_generator = DynamicBarcodeGenerator()
        self.base_url = config.BASE_URL

    async def upload_from_event_inventory(self, db: AsyncSession) -> List[AssignmentInventoryRedisOut]:
        """Simple Redis-to-DB dump with PUT/PATCH semantics and proper type handling"""
        try:
            await db.rollback()  # Start fresh
            inventory_keys = await self.redis.keys("assignment:*")
            
            if not inventory_keys:
                raise HTTPException(status_code=404, detail="No inventory items found in Redis")

            results = []
            
            for key in inventory_keys:
                try:
                    redis_data = await self.redis.get(key)
                    if not redis_data:
                        continue
                    
                    entry_data = json.loads(redis_data)
                    
                    if not entry_data.get("id"):
                        logger.warning(f"Skipping entry without ID from key {key}")
                        continue
                    
                    # Convert only the fields that need conversion
                    processed_data = entry_data.copy()
                    
                    # Convert quantity to string if it's a number
                    if isinstance(processed_data.get('quantity'), (float, int)):
                        processed_data['quantity'] = str(processed_data['quantity'])
                    
                    # Convert date fields to date objects
                    date_fields = ['assigned_date', 'assignment_return_date']
                    for field in date_fields:
                        if field in processed_data and isinstance(processed_data[field], str):
                            try:
                                processed_data[field] = datetime.strptime(
                                    processed_data[field], "%Y-%m-%d"
                                ).date()
                            except ValueError:
                                processed_data[field] = None
                    
                    # Convert datetime fields to datetime objects
                    datetime_fields = ['submission_date']
                    for field in datetime_fields:
                        if field in processed_data and isinstance(processed_data[field], str):
                            try:
                                # Handle both ISO format and space-separated format
                                if 'T' in processed_data[field]:
                                    processed_data[field] = datetime.fromisoformat(
                                        processed_data[field].split('+')[0]
                                    )
                                elif ' ' in processed_data[field]:
                                    processed_data[field] = datetime.strptime(
                                        processed_data[field].split('+')[0], 
                                        '%Y-%m-%d %H:%M:%S.%f'
                                    )
                            except ValueError:
                                processed_data[field] = None
                    
                    # Keep created_at and updated_at as strings (don't convert to datetime)
                    
                    # Check if entry exists
                    existing = await db.get(AssignmentInventory, processed_data["id"])
                    
                    if existing:
                        # PATCH - update existing
                        stmt = (
                            update(AssignmentInventory)
                            .where(AssignmentInventory.id == processed_data["id"])
                            .values(**processed_data)
                        )
                    else:
                        # PUT - create new
                        stmt = insert(AssignmentInventory).values(**processed_data)
                    
                    await db.execute(stmt)
                    results.append(AssignmentInventoryRedisOut(**processed_data))
                    
                except Exception as e:
                    logger.error(f"Error processing key {key}: {str(e)}")
                    continue
            
            await db.commit()
            return results if results else []
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Upload failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload inventory data: {str(e)}"
            )
    
# Create new entry of inventory for to_event which is directly stored in redis
    async def create_assignment_inventory(self, db: AsyncSession, inventory_type: str, item: Union[AssignmentInventoryCreate, dict]) -> AssignmentInventory:
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

            # Convert quantity to integer
            try:
                quantity = int(inventory_data['quantity'])
            except (ValueError, TypeError):
                raise ValueError("quantity must be a valid number")
            
            # Generate barcode if not provided
            if not inventory_data.get('assignment_barcode'):
                try:
                    # Generate minimal barcode with only bars, code, and unique code
                    barcode_value, unique_code, barcode_img = self.barcode_generator.generate_dynamic_barcode({
                        'employee_name': inventory_data['employee_name'],
                        'inventory_id': inventory_data['inventory_id'],
                        'type': inventory_type
                    })

                    # Save barcode image
                    barcode_url = self.barcode_generator.save_barcode_image(
                        barcode_img,
                        inventory_data.get('employee_name'),
                        inventory_data['inventory_id'],
                        inventory_type=inventory_type 
                    )
                    inventory_data.update({
                        'assignment_barcode': barcode_value,
                        'assignment_barcode_unique_code': unique_code,
                        'assignment_barcode_image_url': barcode_url
                    })
                except ValueError as e:
                    logger.error(f"Barcode generation failed: {str(e)}")
                    raise HTTPException(status_code=400, detail=str(e))
                                
            # Update inventory quantities
            try:
                await self.InventoryUpdater.handle_assign_inventory({
                    'name': inventory_data['inventory_name'],
                    'quantity': quantity,
                })
            except Exception as e:
                logger.error(f"Failed to update inventory quantities: {str(e)}")
                raise ValueError(f"Failed to update inventory: {str(e)}")

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
                "wastage_inventory:*",
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
            
            # Determine if this is a return operation
            is_return = update_dict.get('status', '') == 'Returned'
            was_assigned = existing_dict.get('status', '').lower() == 'assigned'
            
            # Calculate quantity adjustment
            quantity_adjustment = 0
            if 'quantity' in update_dict:
                try:
                    new_quantity = int(update_dict['quantity'])
                    old_quantity = int(existing_dict.get('quantity', 0))
                    
                    if is_return and was_assigned:
                        # Full return - use original quantity
                        quantity_adjustment = -old_quantity
                    elif is_return and not was_assigned:
                        # Partial return
                        quantity_adjustment = -(old_quantity - new_quantity)
                    else:
                        # Assignment or quantity change
                        quantity_adjustment = new_quantity - old_quantity
                        
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=400,
                        detail="Quantity must be a valid number"
                    )
                
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
            
            # Update inventory quantities if needed
            if quantity_adjustment != 0:
                try:
                    if is_return:
                        # Use handle_from_event for returns
                        await self.InventoryUpdater.handle_from_event({
                            'name': existing_dict.get('inventory_name'),
                            'RecQty': abs(quantity_adjustment),
                            'is_adjustment': True
                        })
                    else:
                        # Use handle_assign_inventory for assignments
                        await self.InventoryUpdater.handle_assign_inventory({
                            'name': existing_dict.get('inventory_name'),
                            'quantity': quantity_adjustment,
                            'is_adjustment': True
                        })
                except Exception as e:
                    logger.error(f"Failed to update inventory quantities: {str(e)}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to update inventory quantities: {str(e)}"
                    )
            
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
            paginated_projects = projects[skip:skip+1000]  # Assuming page size of 100
            
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
        
#  Show all Assigned Inventory by [employee name, inventory_id] from redis
    async def get_assigned_inventory(
        self,
        employee_name: str,
        inventory_id: str
    ) -> Optional[RedisSearchResult]:
        """
        Get assigned inventory from Redis by employee name and inventory ID
        
        Args:
            employee_name: Name of the employee assigned
            inventory_id: ID of the inventory item
        
        Returns:
            RedisSearchResult if found, None otherwise
        """
        try:
            # Define all possible key patterns where assignments might be stored
            key_patterns = [
                "assignment:*",
                "inventory_assignment:*",
                "assigned_inventory:*",
                "emp_assignments:*",
                "inv_assignments:*"
            ]
            
            # Search through each key pattern
            for pattern in key_patterns:
                async for key in self.redis.scan_iter(match=pattern):
                    data = await self.redis.get(key)
                    if not data:
                        continue

                    try:
                        entry = json.loads(data)
                        # Check if entry matches both criteria
                        if (str(entry.get('employee_name', '')).lower() == employee_name.lower() and 
                            str(entry.get('inventory_id', '')) == inventory_id):
                            # Handle the 'cretaed_at' typo if present
                            if 'cretaed_at' in entry and entry['cretaed_at'] is not None:
                                entry['created_at'] = entry['cretaed_at']
                            
                            # Create RedisSearchResult object
                            validated_data = AssignmentInventoryRedisOut.model_validate(entry)
                            return RedisSearchResult(
                                key=key,
                                data=validated_data
                            )
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.warning(f"Error processing Redis entry {key}: {e}")
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Redis search failed: {str(e)}", exc_info=True)
            raise

