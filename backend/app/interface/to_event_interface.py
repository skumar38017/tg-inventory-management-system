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
    ToEventRedis,
    ToEventRedisOut,
    ToEventRedisUpdate
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
    
        
    async def load_submitted_project_from_db(self, db: AsyncSession, skip: int = 0) -> List[ToEventRedisOut]:
        """
        Retrieve all ToEventInventory entries.
        This method will return a list of ToEventInventoryOut schema instances.
        """
        pass


    async def search_entries_by_project_id(
        self,
        db: AsyncSession,
        search_filter: ToEventInventoryBase
    ) -> List[ToEventRedisOut]:
        """
        Search all entries in local Redis by project_id.
        Returns a list of ToEventRedisOut schema instances.
        """
        pass
    
    # Edit/Update exesting project directly in local Redis
    async def update_to_event_project(
        self, 
        project_id: str,
        update_data: ToEventRedisUpdate
    ) -> Optional[ToEventRedisOut]:
        """
        Update an existing project in local Redis.
        
        This function protects immutable fields (uuid, sno, inventory_id, product_id, created_at)
        and ensures that they cannot be modified.
        
        Args:
            project_id (str): The unique identifier for the project to update.
            update_data (ToEventRedisUpdate): The data used to update the project.
        
        Returns:
            Optional[ToEventRedisOut]: The updated project data after the modification,
                                        or None if the update fails or no changes were made.
        """
        # Logic for updating the project in Redis would go here.
        # This might involve fetching the current project data,
        # applying changes while protecting immutable fields,
        # and then saving the updated data back into Redis.
        
        pass

    async def get_project_by_project_id(
        self, 
        db: AsyncSession, 
        inventory_id: str
    ) -> Optional[ToEventRedisOut]:
        """
        Get inventory entry by its inventory_id (not UUID).
        Returns single ToEventRedisOut instance or None if not found.
        """
        pass

    # ------------------------------------------------------------------------------------------------
    async def update_entry(
        self,
        db: AsyncSession,
        inventory_id: str,
        update_data: ToEventInventoryUpdate
    ) -> Optional[ToEventRedisOut]:
        """
        Update existing inventory entry by inventory_id.
        Protects immutable fields (uuid, sno, inventory_id, product_id, created_at).
        Returns updated ToEventRedisOut instance or None if not found.
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
    ) -> List[ToEventRedisOut]:
        """
        Search inventory items by various criteria.
        Returns filtered list of ToEventRedisOut instances.
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