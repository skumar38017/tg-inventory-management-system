#  backend/app/curd/to_event_inventry_curd.py
from backend.app.utils.common_imports import *

from backend.app.models.to_event_inventry_model import ToEventInventory
from backend.app.schema.to_event_inventry_schma import (
    ToEventInventoryCreate, 
    ToEventRedisUpdateOut,
    ToEventRedisUpdateIn,
    ToEventUploadResponse,
    ToEventUploadSchema,
    RedisInventoryItem,
    ToEventRedisOut,
)
from backend.app.models.to_event_inventry_model import InventoryItem, ToEventInventory
from backend.app.interface.to_event_interface import ToEventInventoryInterface
from backend.app.interface.inventory_updater_interface import InventoryUpdaterInterface

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

redis_client=get_redis()
class ToEventInventoryService(ToEventInventoryInterface, InventoryUpdaterInterface):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.qr_generator = QRCodeGenerator()
        self.barcode_generator = DynamicBarcodeGenerator()
        self.InventoryUpdater = InventoryUpdater(redis_client)
        self.base_url = config.BASE_URL

# upload all to_event_inventory entries from local Redis to the database after click on upload data button
    async def upload_to_event_inventory(self, db: AsyncSession) -> List[ToEventUploadResponse]:
        try:
            # Start with fresh transaction
            await db.rollback()
            
            # Get both types of Redis keys
            inventory_keys = await self.redis.keys("to_event_inventory:*")
            item_keys = await self.redis.keys("inventory_item:*")
            
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
                    
                    redis_data = await self.redis.get(key)
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
                                # PATCH operation - update existing entry with all fields
                                logger.info(f"Updating existing project with project_id: {entry.project_id}")
                                await db.execute(
                                    update(ToEventInventory)
                                    .where(ToEventInventory.project_id == entry.project_id)
                                    .values(**entry_dict)
                                )
                                parent_id = existing.id
                            else:
                                # PUT operation - create new entry
                                logger.info(f"Creating new project with project_id: {entry.project_id}")
                                new_entry = ToEventInventory(**entry_dict)
                                db.add(new_entry)
                                await db.flush()
                                parent_id = new_entry.id

                            # Process inventory items from main entry
                            if entry.inventory_items:
                                for item in entry.inventory_items:
                                    item_data = item.model_dump(exclude={'project_id'})
                                    item_data['project_id'] = parent_id
                                    
                                    # Convert numeric total to string if needed
                                    if isinstance(item_data.get('total'), (int, float)):
                                        item_data['total'] = str(item_data['total'])
                                    
                                    # Check if item already exists
                                    existing_item = await db.execute(
                                        select(InventoryItem)
                                        .where(InventoryItem.id == item.id)
                                    )
                                    existing_item = existing_item.scalar_one_or_none()

                                    if existing_item:
                                        # Update existing item with all fields
                                        await db.execute(
                                            update(InventoryItem)
                                            .where(InventoryItem.id == item.id)
                                            .values(**item_data)
                                        )
                                    else:
                                        # Create new item
                                        new_item = InventoryItem(**item_data)
                                        db.add(new_item)

                            # Commit after each successful project
                            await db.commit()
                            
                            # Prepare success response
                            response = ToEventUploadResponse(
                                success=True,
                                message="Copied to database successfully",
                                project_id=entry.project_id,
                                inventory_items_count=len(entry.inventory_items),
                                created_at=entry.created_at or datetime.now(timezone.utc).isoformat()
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
                    
                    redis_data = await self.redis.get(key)
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

                    # Prepare item data
                    item_data = item.model_dump(exclude={'project_id'})
                    item_data['project_id'] = parent.id
                    
                    # Convert numeric total to string if needed
                    if isinstance(item_data.get('total'), (int, float)):
                        item_data['total'] = str(item_data['total'])

                    # Check if item already exists
                    existing_item = await db.execute(
                        select(InventoryItem)
                        .where(InventoryItem.id == item.id)
                    )
                    existing_item = existing_item.scalar_one_or_none()

                    if existing_item:
                        # Update existing item with all fields
                        await db.execute(
                            update(InventoryItem)
                            .where(InventoryItem.id == item.id)
                            .values(**item_data)
                        )
                    else:
                        # Create new item
                        new_item = InventoryItem(**item_data)
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
                            created_at=datetime.now(timezone.utc).isoformat()
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
    async def create_to_event_inventory(self,  db: AsyncSession, item: ToEventInventoryCreate, inventory_type: str) -> ToEventRedisOut:
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
        
            # Process multiple inventory items (without timestamps)
            inventory_items = []
            for item_data in inventory_data.get('inventory_items', []):
                item_id = str(uuid.uuid4())
                inventory_items.append({
                    **item_data,
                    'id': item_id,
                    'project_id': inventory_data['project_id']  # Only include project_id
                })
    
            # Prepare complete Redis data structure
            redis_data = {
                **inventory_data,
                'inventory_items': inventory_items
            }

            # Generate barcode if not provided
            if not inventory_data.get('to_event'):
                try:
                    # Generate minimal barcode with only bars, code, and unique code
                    barcode_value, unique_code, barcode_img = self.barcode_generator.generate_dynamic_barcode({
                        'project_name': inventory_data['project_name'],
                        'project_id': inventory_data['project_id'],
                        'type': inventory_data
                    })

                    # Save barcode image
                    barcode_url = self.barcode_generator.save_barcode_image(
                        barcode_img,
                        inventory_data.get('project_name'),
                        inventory_data.get('project_id'),
                        inventory_type=inventory_type 
                    )
                    inventory_data.update({
                        'project_barcode': barcode_value,
                        'project_barcode_unique_code': unique_code,
                        'project_barcode_image_url': barcode_url
                    })
                except ValueError as e:
                    logger.error(f"Barcode generation failed: {str(e)}")
                    raise HTTPException(status_code=400, detail=str(e))
            
            # Prepare complete Redis data structure (AFTER barcode generation)
            redis_data = {
                **inventory_data,  # This now includes barcode info
                'inventory_items': inventory_items
            }

            # Store main inventory in Redis
            await self.redis.set(
                f"to_event_inventory:{inventory_data['project_id']}",
                json.dumps(redis_data, default=str)
            )
    
            # Store individual items with their own keys (still without timestamps)
            for item in inventory_items:
                await self.redis.set(
                    f"inventory_item:{item['id']}",
                    json.dumps(item, default=str)
                )

                await self.InventoryUpdater.handle_to_event({
                    'name': item.get('name'),  
                    'total': item.get('total', 0)  
                })
   
        except Exception as e:
            logger.error(f"Redis storage failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create inventory: {str(e)}"
            )
        finally:
            return ToEventRedisOut(**redis_data)
    
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
            paginated_projects = projects[skip:skip+250]  # Assuming page size of 100
            
            return paginated_projects
        except Exception as e:
            logger.error(f"Redis error fetching entries: {e}")
            raise HTTPException(status_code=500, detail="Redis error")
    
    #  show all project directly from local Redis in `submitted Forms` directly after submitting the form
    async def get_project_data(self, project_id: str):
        try:
            redis_key = f"to_event_inventory:{project_id}"
            # Use get() instead of keys() to retrieve the actual value
            existing_data = await self.redis.get(redis_key)

            if not existing_data:
                return None

            # Parse the JSON data from Redis
            project_dict = json.loads(existing_data)
            
            # Ensure inventory_items is properly formatted
            if 'inventory_items' in project_dict:
                if isinstance(project_dict['inventory_items'], str):
                    try:
                        project_dict['inventory_items'] = json.loads(project_dict['inventory_items'])
                    except json.JSONDecodeError:
                        project_dict['inventory_items'] = []
                elif not isinstance(project_dict['inventory_items'], list):
                    project_dict['inventory_items'] = []
                    
            return ToEventRedisOut(**project_dict)
        
        except Exception as e:
            logger.error(f"Error fetching project {project_id} from Redis: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")

# Update record in existing project in Redis and update `inventory Quantity` in Inventory acording to operation
    async def update_project_data(self, project_id: str, update_data: ToEventRedisUpdateIn):
        try:
            redis_key = f"to_event_inventory:{project_id}"

            # Protected fields that shouldn't be changed
            protected_fields = [
                'id', 'project_id', 'uuid', 'created_at', 'cretaed_at',
                'project_barcode', 'project_barcode_unique_code',
                'project_barcode_image_url'
            ]

            # Fetch existing project data from Redis
            existing_data = await self.redis.get(redis_key)  # Changed from keys() to get()
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
                    existing_items = {item['sno']: item for item in existing_dict.get('inventory_items', [])}
                    
                    updated_items = []
                    for new_item in update_dict['inventory_items']:
                        # If item exists, preserve its ID and project_id
                        # Calculate quantity difference for inventory updates
                        quantity_diff = 0

                        # If item exists, preserve its ID and project_id
                        if 'sno' in new_item and new_item['sno'] in existing_items:
                            existing_item = existing_items[new_item['sno']]
                            new_item['id'] = existing_item.get('id')
                            new_item['project_id'] = existing_item.get('project_id')
                
                            # Calculate the difference between old and new total
                            old_total = existing_item.get('total', 0)
                            new_total = new_item.get('total', 0)
                            quantity_diff = new_total - old_total
                        else:
                            # If new item, generate ID, set project_id and use the full quantity
                            new_item['id'] = str(uuid.uuid4())
                            new_item['project_id'] = project_id
                            quantity_diff = new_item.get('total', 0)
                    
                    # Update inventory if there's a quantity change
                    if quantity_diff != 0 and 'name' in new_item:
                        try:
                            await self.InventoryUpdater.handle_to_event({
                                'name': new_item['name'],
                                'total': quantity_diff,
                                'inventory_id': new_item.get('inventory_id'),
                                'is_adjustment': True  # This tells it to treat as adjustment
                            })
                        except Exception as e:
                            logger.error(f"Failed to update inventory for {new_item.get('name')}: {str(e)}")

                        # Continue with project update even if inventory update fails
                        # You might want to handle this differently based on requirements
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
            await self.redis.set(
                redis_key,
                validated_data.model_dump_json()
            )

            return validated_data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")
        