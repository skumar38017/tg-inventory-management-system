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
    DateRangeFilter
)
from sqlalchemy.exc import SQLAlchemyError
from backend.app.interface.entry_inverntory_interface import EntryInventoryInterface
import logging
from fastapi import HTTPException
from typing import List, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

class EntryInventoryService(EntryInventoryInterface):
    """Implementation of EntryInventoryInterface with async operations"""


    async def create_entry_inventory(self, db: AsyncSession, entry_inventory: EntryInventoryCreate) -> EntryInventory:
        if db is None:
            raise ValueError("Database session is None")
        
        try:
            # Convert to dict and ensure timestamps are set
            entry_data = entry_inventory.model_dump()
            if 'created_at' not in entry_data or entry_data['created_at'] is None:
                entry_data['created_at'] = datetime.now(timezone.utc)
            if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
                entry_data['updated_at'] = datetime.now(timezone.utc)
            new_entry = EntryInventory(**entry_inventory.dict())

            new_entry = EntryInventory(**entry_data)
            db.add(new_entry)
            await db.commit()
            await db.refresh(new_entry)
            return new_entry
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=400, detail=str(e))

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

    #  Search inventory items by various criteria {Product ID, Inventory ID}
    async def search_entries(self, db: AsyncSession, search_filter: EntryInventorySearch) -> List[EntryInventoryOut]:
        try:
            query = select(EntryInventory)
            
            if search_filter.inventory_id:
                query = query.where(EntryInventory.inventory_id == search_filter.inventory_id)
            if search_filter.product_id:
                query = query.where(EntryInventory.product_id == search_filter.product_id)
            # Add other filters as needed
                
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error searching entries: {e}")
            raise HTTPException(status_code=500, detail="Database error")
        
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
                .where(EntryInventory.created_at.between(start_datetime, end_datetime))
                .order_by(EntryInventory.created_at)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error filtering by date: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    #  List all inventory directly from database after clicking {sync} button
    async def list_all_entries(self, db: AsyncSession) -> List[EntryInventoryOut]:
        try:
            result = await db.execute(
                select(EntryInventory).order_by(EntryInventory.name)
            )
            entries = result.scalars().all()

            # Convert SQLAlchemy models to Pydantic models
            return [
                EntryInventoryOut.model_validate(entry)
                for entry in entries
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error listing entries: {e}")
            raise HTTPException(
                status_code=500,
                detail="Database operation failed"
            )
        except Exception as e:
            logger.error(f"Unexpected error listing entries: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve inventory data"
            )