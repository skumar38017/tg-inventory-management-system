#  backend/app/interface/entry_inventory_interface.py

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import List, Optional
from fastapi import HTTPException, Request
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryCreate,
    EntryInventoryUpdateOut,
    EntryInventoryUpdate,
    StoreInventoryRedis,
    InventoryRedisOut,
    EntryInventorySearch,
    DateRangeFilter,
    DateRangeFilterOut,
)
from pydantic import BaseModel
from datetime import date
import requests

class GoogleSheetsToRedisSyncInterface:
    #  Store all recored in Redis after clicking {sync} button
    async def sync_inventory_from_google_sheets(self, request: Request) -> List[InventoryRedisOut]:
        """
        Sync inventory data from Google Sheets to Redis
        
        Returns:
            bool: True if sync was successful
            
        Raises:
            HTTPException: If sync fails
        """
        pass

class EntryInventoryInterface:
    """Interface for EntryInventory operations with immutable core fields."""
    
    async def create_entry_inventory(self, db: AsyncSession, entry_inventory: EntryInventoryCreate) -> EntryInventory:
        """
        Create a new EntryInventory entry.
        This method will receive an EntryInventoryCreate schema instance
        and return a created EntryInventory instance.
        """
        pass
    
    async def get_all_entries(self, db: AsyncSession, skip: int = 0) -> List[EntryInventoryUpdateOut]:
        """
        Retrieve all EntryInventory entries.
        This method will return a list of EntryInventoryOut schema instances.
        """
        pass
    
    async def get_by_inventory_id(
        self, 
        db: AsyncSession, 
        inventory_id: str
    ) -> Optional[EntryInventoryUpdateOut]:
        """
        Get inventory entry by its inventory_id (not UUID).
        Returns single EntryInventoryUpdateOut instance or None if not found.
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
    ) -> List[EntryInventoryUpdateOut]:
        """
        Search inventory entries by various criteria.
        Returns filtered list of EntryInventoryUpdateOut instances.
        """
        pass

    async def get_by_date_range(
        self,
        db: AsyncSession,
        date_range_filter: DateRangeFilter
    ) -> List[DateRangeFilterOut]:
        """
        Get inventory entries within a date range.
        Returns list of DateRangeFilterOut instances filtered by date range.
        """
        pass

    async def store_inventory_in_redis(
        self, 
        db: AsyncSession
    ) -> List[StoreInventoryRedis]:
        """
        Store all inventory entries in Redis.
        Returns complete list of StoreInventoryRedis instances.
        """
        pass

    async def list_entry_inventories_curd(
        self, 
        db: AsyncSession
    ) -> List[InventoryRedisOut]:
        """
        Get all inventory entries from Redis.
        Returns complete list of InventoryRedisOut instances ordered by name.
        """
        pass