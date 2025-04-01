# backend/app/routers/entry_inventory_curd.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.schema.entry_inventory_schema import EntryInventoryCreate, EntryInventoryUpdate
from sqlalchemy.exc import SQLAlchemyError
from backend.app.interface.entry_inverntory_interface import EntryInventoryInterface
import logging
from fastapi import APIRouter, HTTPException, Depends

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

class EntryInventoryService(EntryInventoryInterface):
    async def create_entry_inventory_curd(self, db: AsyncSession, entry_inventory: EntryInventoryCreate):
        if db is None:
            raise ValueError("Database session is None")
        
        try:
            new_entry = EntryInventory(**entry_inventory.dict())
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

    # READ: Get an inventory entry by its inventry_id
    async def get_inventory_by_inventry_id_curd(self, db: AsyncSession, inventory_id: str):
        try:
            result = await db.execute(select(EntryInventory).filter(EntryInventory.inventory_id == inventory_id))
            entry_inventory = result.scalar_one_or_none()
            return entry_inventory
        except SQLAlchemyError as e:
            logger.error(f"Error fetching entry inventory: {e}")
            raise e

    # READ ALL: Get all inventory entries
    async def get_all_entry_inventory_curd(db: AsyncSession):
        try:
            result = await db.execute(select(EntryInventory))
            entry_inventory_list = result.scalars().all()
            return entry_inventory_list
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all entry inventories: {e}")
            raise e

    # UPDATE: Update an existing inventory entry
    async def update_inventory_item_curd(db: AsyncSession, inventry_id: str, entry_inventory_update: EntryInventoryUpdate):
        try:
            result = await db.execute(select(EntryInventory).filter(EntryInventory.inventory_id == inventry_id))
            entry_inventory = result.scalar_one_or_none()

            if not entry_inventory:
                return None

            # Update the fields
            for key, value in entry_inventory_update.dict(exclude_unset=True).items():
                setattr(entry_inventory, key, value)

            async with db.begin():
                await db.commit()  # Commit asynchronously
                await db.refresh(entry_inventory)  # Refresh the object to get updated values

            return entry_inventory
        except SQLAlchemyError as e:
            logger.error(f"Error updating entry inventory: {e}")
            raise e

    # DELETE: Delete an inventory entry
    async def delete_inventory_iten_curd(db: AsyncSession, inventry_id: str):
        try:
            result = await db.execute(select(EntryInventory).filter(EntryInventory.inventory_id == inventry_id))
            entry_inventory = result.scalar_one_or_none()

            if not entry_inventory:
                return None

            async with db.begin():
                await db.delete(entry_inventory)
                await db.commit()

            return entry_inventory
        except SQLAlchemyError as e:
            logger.error(f"Error deleting entry inventory: {e}")
            raise e

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
