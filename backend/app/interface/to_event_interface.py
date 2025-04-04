# app/interface/to_event_interface.py
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import List, Optional
from backend.app.models.to_event_inventry_model import ToEventInventory
from backend.app.schema.to_event_inventry_schma import (
    ToEventInventoryBase,
    ToEventInventoryCreate,
    ToEventInventoryOut,
    ToEventInventoryUpdate,
    ToEventInventoryUpdateOut,
    ToEventRedis,
    ToEventRedisOut,
)
from pydantic import BaseModel
from datetime import date

class ToEventInventoryInterface:
    """Interface for ToEventInventory operations with immutable core fields."""
    
    # # Upload all `to_event_inventory` entries from local Redis to the database after click on `upload data` button
    async def upload_to_event_inventory(self, db: AsyncSession, skip: int = 0) -> List[ToEventRedisOut]:
        """
        Upload all `to_event_inventory` entries from local Redis to the database.
        Returns a list of ToEventRedisOut schema instances.
        """
        raise NotImplementedError
   
   
    async def create_to_event_inventory(self, db: AsyncSession, to_event_inventory: ToEventInventoryCreate) -> ToEventInventory:
        """
        Create a new ToEventInventory entry.
        This method will receive an ToEventInventoryCreate schema instance
        and return a created ToEventInventory instance.
        """
        pass
    
        
    async def get_all_entries(self, db: AsyncSession, skip: int = 0) -> List[ToEventInventoryUpdateOut]:
        """
        Retrieve all ToEventInventory entries.
        This method will return a list of ToEventInventoryOut schema instances.
        """
        pass
    
    async def get_project_by_project_id(
        self, 
        db: AsyncSession, 
        inventory_id: str
    ) -> Optional[ToEventInventoryUpdateOut]:
        """
        Get inventory entry by its inventory_id (not UUID).
        Returns single ToEventInventoryUpdateOut instance or None if not found.
        """
        pass

    async def update_entry(
        self,
        db: AsyncSession,
        inventory_id: str,
        update_data: ToEventInventoryUpdate
    ) -> Optional[ToEventInventoryUpdateOut]:
        """
        Update existing inventory entry by inventory_id.
        Protects immutable fields (uuid, sno, inventory_id, product_id, created_at).
        Returns updated ToEventInventoryUpdateOut instance or None if not found.
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
        search_filter: ToEventInventoryBase
    ) -> List[ToEventInventoryUpdateOut]:
        """
        Search inventory items by various criteria.
        Returns filtered list of ToEventInventoryUpdateOut instances.
        """
        pass

    # async def get_by_date_range(
    #     self,
    #     db: AsyncSession,
    #     date_range_filter: DateRangeFilter
    # ) -> List[DateRangeFilterOut]:
    #     """
    #     Get inventory items within a date range.
    #     Returns list of DateRangeFilterOut instances filtered by date range.
    #     """
    #     pass

    async def store_project_in_redis(
        self, 
        db: AsyncSession
    ) -> List[ToEventRedis]:
        """
        Store all inventory entries in Redis.
        Returns complete list of StoreInventoryRedis instances.
        """
        pass

    async def show_all_project_from_redis(
        self, 
        db: AsyncSession
    ) -> List[ToEventRedisOut]:
        """
        Get all inventory entries from Redis.
        Returns complete list of InventoryRedisOut instances ordered by name.
        """
        pass