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
from fastapi import HTTPException
from typing import List, Optional
from backend.app.database.redisclient import redis_client
from backend.app import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

class EntryInventoryService(EntryInventoryInterface):
    """Implementation of EntryInventoryInterface with async operations"""
    def __init__(self, base_url: str = config.BASE_URL):
        self.base_url = base_url  # Your server's base URL

    #  Create new entry
    async def create_entry_inventory(self, db: AsyncSession, entry_data: dict) -> EntryInventory:
        if db is None:
            raise ValueError("Database session is None")

        try:
            # Convert boolean fields to string "true"/"false"
            for field in ['on_rent', 'rented_inventory_returned', 'on_event', 'in_office', 'in_warehouse']:
                if field in entry_data:
                    val = entry_data[field]
                    if isinstance(val, bool):
                        entry_data[field] = "true" if val else "false"
                    elif isinstance(val, str):
                        entry_data[field] = val.lower()
                    else:
                        entry_data[field] = "false"

            # Remove auto-generated fields if present
            for field in ['bar_code', 'unique_code', 'created_at', 'updated_at', 'uuid']:
                entry_data.pop(field, None)

            # Create new instance
            new_entry = EntryInventory(**entry_data)

            db.add(new_entry)
            await db.commit()
            await db.refresh(new_entry)

            return new_entry

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

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

    # READ ALL: Get all inventory entries
    async def get_all_entries(self, db: AsyncSession, skip: int = 0) -> List[EntryInventoryOut]:
        try:
            result = await db.execute(
                select(EntryInventory)
                .order_by(EntryInventory.name)  # Alphabetical order
                .offset(skip)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching entries: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    # READ: Get an inventory entry by its inventry_id
    async def get_by_inventory_id(self, db: AsyncSession, inventory_id: str) -> Optional[EntryInventoryOut]:
        try:
            result = await db.execute(
                select(EntryInventory)
                .where(EntryInventory.inventory_id == inventory_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching entry: {e}")
            raise HTTPException(status_code=500, detail="Database error")

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
                    name=entry.name,
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
