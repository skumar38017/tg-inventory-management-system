#  backend/app/interface/entry_inventory_interface.py

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import List, Optional
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryCreate,
    EntryInventoryUpdate,
    EntryInventoryOut,
    EntryInventorySearch,
    DateRangeFilter
)
from pydantic import BaseModel
from datetime import date

class EntryInventoryInterface:
    """Interface for EntryInventory operations."""
    
    async def create_entry_inventory(self, db: AsyncSession, entry_inventory: EntryInventoryCreate) -> EntryInventory:
        """
        Create a new EntryInventory entry.
        This method will receive an EntryInventoryCreate schema instance
        and return a created EntryInventory instance.
        """
        pass
    
    async def get_all_entries(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[EntryInventoryOut]:
        """
        Retrieve all EntryInventory entries.
        This method will return a list of EntryInventoryOut schema instances.
        """
        pass
    
    async def get_by_inventory_id(self, db: AsyncSession, inventory_id: str) -> Optional[EntryInventoryOut]:
        """
        Get EntryInventory entry by its UUID.
        This method will return a single EntryInventoryOut instance or None.
        """
        pass
    
    async def update_entry(self, db: AsyncSession, uuid: str, entry_inventory: EntryInventoryUpdate) -> Optional[EntryInventory]:
        """
        Update an existing EntryInventory entry by its UUID.
        This method will receive an EntryInventoryUpdate schema instance and return the updated EntryInventory instance.
        """
        pass
    
    async def delete_entry(self, db: AsyncSession, uuid: str) -> bool:
        """
        Delete an EntryInventory entry by its UUID.
        This method will return True if the entry is successfully deleted, False otherwise.
        """
        pass

    async def search_entries(self, db: AsyncSession, search_filter: EntryInventorySearch) -> List[EntryInventoryOut]:
        """
        Search for EntryInventory entries based on the provided search filter.
        This method will return a list of EntryInventoryOut schema instances.
        """
        pass

    async def get_by_date_range(self, db: AsyncSession, date_range_filter: DateRangeFilter) -> List[EntryInventoryOut]:
        pass

    async def list_all_entries(self, db: AsyncSession) -> List[EntryInventoryOut]:
        """
        Get EntryInventory entries by date range.
        This method will return a list of EntryInventoryOut schema instances.
        """
        pass