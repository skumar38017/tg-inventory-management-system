#  backend/app/interface/entry_inventory_interface.py

from sqlalchemy.orm import Session
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
    
    def create_entry_inventory(self, db: Session, entry_inventory: EntryInventoryCreate) -> EntryInventory:
        """
        Create a new EntryInventory entry.
        This method will receive an EntryInventoryCreate schema instance
        and return a created EntryInventory instance.
        """
        pass
    
    def get_entries_inventory(self, db: Session, skip: int = 0, limit: int = 100) -> List[EntryInventoryOut]:
        """
        Retrieve all EntryInventory entries.
        This method will return a list of EntryInventoryOut schema instances.
        """
        pass
    
    def get_entry_inventory_by_inventry_id_interface(self, db: Session, inventory_id: str) -> Optional[EntryInventoryOut]:
        """
        Get EntryInventory entry by its UUID.
        This method will return a single EntryInventoryOut instance or None.
        """
        pass
    
    def update_entry_inventory(self, db: Session, uuid: str, entry_inventory: EntryInventoryUpdate) -> Optional[EntryInventory]:
        """
        Update an existing EntryInventory entry by its UUID.
        This method will receive an EntryInventoryUpdate schema instance and return the updated EntryInventory instance.
        """
        pass
    
    def delete_entry_inventory(self, db: Session, uuid: str) -> bool:
        """
        Delete an EntryInventory entry by its UUID.
        This method will return True if the entry is successfully deleted, False otherwise.
        """
        pass

    def search_inventory_interface(self, db: Session, search_filter: EntryInventorySearch) -> List[EntryInventoryOut]:
        """
        Search for EntryInventory entries based on the provided search filter.
        This method will return a list of EntryInventoryOut schema instances.
        """
        pass

    def get_entry_inventory_by_date_range_curd(self, db: Session, date_range_filter: DateRangeFilter) -> List[EntryInventoryOut]:
        """
        Get EntryInventory entries by date range.
        This method will return a list of EntryInventoryOut schema instances.
        """
        pass