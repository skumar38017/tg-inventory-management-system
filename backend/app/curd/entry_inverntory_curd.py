# backend/app/routers/entry_inventory_curd.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, time, timedelta, timezone
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryCreate, 
    EntryInventoryUpdate,
    EntryInventoryOut,
    EntryInventorySearch,
    InventoryRedisOut,
    StoreInventoryRedis,
    DateRangeFilter
)
from sqlalchemy.exc import SQLAlchemyError
from backend.app.interface.entry_inverntory_interface import EntryInventoryInterface
import logging
import uuid
from fastapi import HTTPException
from typing import List, Optional
from backend.app.database.redisclient import redis_client
from backend.app import config
from backend.app.utils.barcode_generator import BarcodeGenerator
from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError

from typing import Union
import json
import redis.asyncio as redis
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

class EntryInventoryService(EntryInventoryInterface):
    """Implementation of EntryInventoryInterface with async operations"""
    def __init__(self, base_url: str = config.BASE_URL, redis_client: redis.Redis = redis_client):
        self.base_url = base_url
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()

# Create new entry of inventory for to_event which is directly stored in redis
    async def create_entry_inventory(self,  db: AsyncSession, entry_data: EntryInventoryCreate) -> EntryInventory:
        """
        Create a new inventory entry stored permanently in Redis (no database storage).
        
        Args:
            entry_data: Inventory data to be stored
            
        Returns:
            EntryInventory: The created inventory object
            
        Raises:
            HTTPException: If there's a validation or storage error
        """
        try:
            # Convert input data to dictionary
            if isinstance(entry_data, EntryInventoryCreate):
                inventory_data = entry_data.model_dump(exclude_unset=True)
            else:
                inventory_data = entry_data

            # Generate ID if not provided
            if not inventory_data.get('id'):
                inventory_id = str(uuid.uuid4())
                inventory_data['id'] = inventory_id

            # Set timestamps
            current_time = datetime.now(timezone.utc)
            inventory_data['updated_at'] = current_time
            inventory_data['created_at'] = current_time 

            # Process and validate boolean fields
            boolean_fields = {
                'on_rent': False,
                'rented_inventory_returned': False,
                'on_event': False,
                'in_office': False,
                'in_warehouse': False
            }

            for field, default_value in boolean_fields.items():
                val = inventory_data.get(field, default_value)
                if isinstance(val, bool):
                    inventory_data[field] = "true" if val else "false"
                elif isinstance(val, str):
                    inventory_data[field] = val.lower()
                else:
                    inventory_data[field] = "false"

            # Generate barcode if not provided
            if not inventory_data.get('inventory_barcode'):
                barcode_data = {
                    'inventory_name': inventory_data['inventory_name'],
                    'inventory_id': inventory_data['inventory_id'],
                    'id': inventory_id 
                }
                barcode, unique_code = self.barcode_generator.generate_linked_codes(barcode_data)
                inventory_data.update({
                    'inventory_barcode': barcode,
                    'inventory_unique_code': unique_code,
                    'inventory_barcode_url': inventory_data.get('inventory_barcode_url', "")
                })

            # Permanent Redis storage (no expiration)
            redis_key = f"inventory:{inventory_data['inventory_name']}{inventory_data['inventory_id']}"
            await self.redis.set(
                redis_key,
                json.dumps(inventory_data, default=str)
            )
            return EntryInventory(**inventory_data)

        except KeyError as ke:
            logger.error(f"Missing required field: {str(ke)}")
            raise HTTPException(status_code=400, detail=f"Missing required field: {str(ke)}")
        except json.JSONEncodeError as je:
            logger.error(f"JSON encoding error: {str(je)}")
            raise HTTPException(status_code=400, detail="Invalid inventory data format")
        except Exception as e:
            logger.error(f"Redis storage failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create inventory assignment: {str(e)}"
            )

    #  Filter inventory by date range without any `IDs`
    async def get_by_date_range(
        self,
        db: AsyncSession,
        date_range_filter: DateRangeFilter
    ) -> List[EntryInventory]:
        try:
            # Convert dates to datetime at start/end of day
            start_datetime = datetime.combine(date_range_filter.from_date, time.min)
            end_datetime = datetime.combine(date_range_filter.to_date, time.max)

            result = await db.execute(
                select(EntryInventory)
                .where(EntryInventory.updated_at.between(start_datetime, end_datetime))
                .order_by(EntryInventory.updated_at)
            )
            entries = result.scalars().all()
              # Convert to Pydantic models with proper null handling
            return [EntryInventoryOut.from_orm(entry) for entry in entries]
        except SQLAlchemyError as e:
            logger.error(f"Database error filtering by date: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    # READ ALL: Get all inventory entries directly from redis
    async def get_all_entries(self, db: AsyncSession, skip: int = 0) -> List[InventoryRedisOut]:
        try:
            # Get all keys matching your project pattern
            keys = await self.redis.keys("inventory:*")
            
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
                        validated_project = InventoryRedisOut.model_validate(assigned_data)
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
    # READ: Get an inventory entry by its inventry_id
    async def get_by_inventory_id(self, db: AsyncSession, inventory_id: str) -> Optional[EntryInventoryOut]:
        try:
            # Search all inventory keys in Redis
            keys = await self.redis.keys("inventory:*")
            
            for key in keys:
                # Get the inventory data from Redis
                inventory_data = await self.redis.get(key)
                if inventory_data:
                    data = json.loads(inventory_data)
                    # Check if this is the inventory we're looking for
                    if data.get('inventory_id') == inventory_id:
                        # Convert string timestamps back to datetime objects
                        if 'updated_at' in data:
                            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                        return EntryInventoryOut(**data)
            
            return None  # Return None if not found

        except json.JSONDecodeError as je:
            logger.error(f"Error decoding Redis data: {str(je)}")
            raise HTTPException(
                status_code=500,
                detail="Error decoding inventory data"
            )
        except Exception as e:
            logger.error(f"Redis error fetching inventory: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error fetching inventory from Redis"
            )

    # UPDATE: Update an existing inventory entry {} {Inventory ID}
    async def update_entry(self, db: AsyncSession, inventory_id: str, update_data: EntryInventoryUpdate):
        try:
            result = await db.execute(
                select(EntryInventory)
                .where(EntryInventory.inventory_id == inventory_id)
            )
            entry = result.scalar_one_or_none()

            if not entry:
                return None

            update_dict = update_data.model_dump(exclude_unset=True)
            IMMUTABLE_FIELDS = ['uuid', 'sno', 'inventory_id', 'product_id', 'created_at']

            # Update mutable fields
            for field, value in update_dict.items():
                if field not in IMMUTABLE_FIELDS:
                    setattr(entry, field, value)

            # Always update timestamp
            entry.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(entry)
            return entry

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating entry: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    # DELETE: Delete an inventory entry by  {Inventory ID}
    async def delete_entry(self, db: AsyncSession, inventory_id: str) -> bool:
        try:
            result = await db.execute(
                select(EntryInventory)
                .where(EntryInventory.inventory_id == inventory_id)
            )
            entry = result.scalar_one_or_none()
            
            if not entry:
                return False
                
            await db.delete(entry)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting entry: {e}")
            raise HTTPException(status_code=500, detail="Database error")
        
    # Search inventory items by various criteria {Product ID, Inventory ID, Project ID}
    async def search_entries(
        self, 
        db: AsyncSession, 
        search_filter: EntryInventorySearch
    ) -> List[EntryInventoryOut]:
        """
        Search inventory entries by exactly one of:
        - inventory_id
        - product_id
        - project_id
        """
        try:
            query = select(EntryInventory)

            if search_filter.inventory_id:
                query = query.where(EntryInventory.inventory_id == search_filter.inventory_id)
            elif search_filter.product_id:
                query = query.where(EntryInventory.product_id == search_filter.product_id)
            else:  # project_id
                query = query.where(EntryInventory.project_id == search_filter.project_id)

            result = await db.execute(query)
            entries = result.scalars().all()

            return [EntryInventoryOut.from_orm(entry) for entry in entries]

        except SQLAlchemyError as e:
            logger.error(f"Database error searching entries: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Database error while searching inventory items"
            )
        
# ------------------------------------------------------------------------------------------------------------------------------------------------
#  inventory entries directly from local databases  (no search) according in sequence alphabetical order after clicking `Show All` button
# ------------------------------------------------------------------------------------------------------------------------------------------------

    #  Store all recored in Redis after clicking {sync} button
    async def store_inventory_in_redis(self, db: AsyncSession) -> bool:
        """Store all inventory entries in Redis"""
        try:
            # Get all entries from database
            entries = await db.execute(select(EntryInventory))
            entries = entries.scalars().all()
            
            # Convert to Redis storage format and store
            for entry in entries:
                redis_entry = StoreInventoryRedis(
                    uuid=entry.uuid,
                    sno=entry.sno,
                    inventory_id=entry.inventory_id,
                    product_id=entry.product_id,
                    inventory_name=entry.inventory_name,
                    material=entry.material,
                    total_quantity=entry.total_quantity,
                    manufacturer=entry.manufacturer,
                    purchase_dealer=entry.purchase_dealer,
                    purchase_date=entry.purchase_date,
                    purchase_amount=entry.purchase_amount,
                    repair_quantity=entry.repair_quantity,
                    repair_cost=entry.repair_cost,
                    on_rent=entry.on_rent,
                    vendor_name=entry.vendor_name,
                    total_rent=entry.total_rent,
                    rented_inventory_returned=entry.rented_inventory_returned,
                    on_event=entry.on_event,
                    in_office=entry.in_office,
                    in_warehouse=entry.in_warehouse,
                    issued_qty=entry.issued_qty,
                    balance_qty=entry.balance_qty,
                    submitted_by=entry.submitted_by,
                    bar_code=entry.bar_code,
                    barcode_image_url=entry.barcode_image_url,
                    created_at=entry.created_at,
                    updated_at=entry.updated_at
                )
            
                await redis_client.set(
                    f"inventory:{entry.inventory_id}", 
                    redis_entry.json()
                )
            
            logger.info(f"Stored {len(entries)} entries in Redis")
            return True
        except Exception as e:
            logger.error(f"Redis storage error: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to sync with Redis"
            )

    #  Show all inventory entries directly from local Redis after clicking {Show All} button
    async def show_all_inventory_from_redis(self) -> List[InventoryRedisOut]:
        """Retrieve all inventory entries from Redis"""
        try:
            # Get all inventory keys from Redis
            keys = await redis_client.keys("inventory:*")

            # Retrieve and parse all entries
            entries = []
            for key in keys:
                data = await redis_client.get(key)
                if data:
                    entries.append(InventoryRedisOut.from_redis(data))

            # Sort by name (alphabetical)
            entries.sort(key=lambda x: x.name)
            return entries

        except Exception as e:
            logger.error(f"Redis retrieval error: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to load from Redis"
            )

    # List all inventory entries function
    async def list_entry_inventories_curd(self, db: AsyncSession):
        try:
            # Execute query to fetch all entries
            result = await db.execute(select(EntryInventory))
            # Retrieve all rows as a list
            entry_inventory_list = result.scalars().all()
            return entry_inventory_list
        except SQLAlchemyError as e:
            logger.error(f"Error listing entry inventories: {e}")
            raise e
