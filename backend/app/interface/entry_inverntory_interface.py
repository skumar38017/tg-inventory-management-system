#  backend/app/interface/entry_inventory_interface.py

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import List, Optional
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryCreate,
    EntryInventoryUpdateOut,
    EntryInventoryUpdate,
    EntryInventoryOut,
    EntryInventorySearch,
    DateRangeFilter
)
from pydantic import BaseModel
from datetime import date

class EntryInventoryInterface:
    """Interface for EntryInventory operations with immutable core fields."""
    
    async def create_entry_inventory(self, db: AsyncSession, entry_inventory: EntryInventoryCreate) -> EntryInventory:
        """
        Create a new EntryInventory entry.
        This method will receive an EntryInventoryCreate schema instance
        and return a created EntryInventory instance.
        """
        pass
    
    async def get_all_entries(self, db: AsyncSession, skip: int = 0) -> List[EntryInventoryOut]:
        """
        Retrieve all EntryInventory entries.
        This method will return a list of EntryInventoryOut schema instances.
        """
        pass
    
    async def get_by_inventory_id(
        self, 
        db: AsyncSession, 
        inventory_id: str
    ) -> Optional[EntryInventoryOut]:
        """
        Get inventory entry by its inventory_id (not UUID).
        Returns single EntryInventoryOut instance or None if not found.
        """
        pass
    
    async def update_entry(
        self,
        db: AsyncSession,
        inventory_id: str,
        update_data: EntryInventoryUpdate
    ) -> Optional[EntryInventoryUpdateOut]:
        """
        Update existing inventory entry by inventory_id.
        Protects immutable fields (uuid, sno, inventory_id, product_id, created_at).
        Returns updated EntryInventoryUpdateOut instance or None if not found.
        """
        pass
    
    async def delete_entry(
        self, 
        db: AsyncSession, 
        inventory_id: str  # Using inventory_id instead of UUID
    ) -> bool:
        """
        Delete inventory entry by inventory_id.
        Returns True if deleted successfully, False if not found.
        """
        pass

    async def search_entries(
        self,
        db: AsyncSession,
        search_filter: EntryInventorySearch
    ) -> List[EntryInventoryOut]:
        """
        Search inventory entries by various criteria.
        Returns filtered list of EntryInventoryOut instances.
        """
        pass

    async def get_by_date_range(
        self,
        db: AsyncSession,
        date_range_filter: DateRangeFilter
    ) -> List[EntryInventoryOut]:
        """
        Get inventory entries within a date range.
        Returns list of EntryInventoryOut instances filtered by date range.
        """
        pass

    async def list_all_entries(
        self, 
        db: AsyncSession
    ) -> List[EntryInventoryOut]:
        """
        Get all inventory entries without pagination.
        Returns complete list of EntryInventoryOut instances ordered by name.
        """
        pass