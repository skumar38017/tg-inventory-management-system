#  backend/app/interface/assign_inventory_interface.py
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import List, Optional
from backend.app.models.assign_inventory_model import AssignmentInventory
from backend.app.schema.wastage_inventory_schema import (
    WastageInventoryBase,
    WastageInventoryCreate,
    WastageInventoryOut,
    WastageInventoryUpdate,
    WastageInventoryRedisIn,
    WastageInventoryRedisOut,
    WastageInventorySearch,

)
from pydantic import BaseModel
from datetime import date, datetime
from backend.app.models.wastege_inventory_model import WastageInventory

from datetime import date

class WastageInventoryInterface:
    """Interface for AssignmentInventory operations with immutable core fields."""
    
    # # Upload all `assignment_inventory` entries from local Redis to the database after click on `upload data` button
    async def upload_wastage_inventory(self, db: AsyncSession, skip: int = 0) -> List[WastageInventoryRedisOut]:
        """Upload all wastage inventory entries from Redis to database with bulk upsert.
        Returns a list of WastageInventoryRedisOut schema instances.
        """
        raise NotImplementedError
   
   
    async def create_wastage_inventory(self, db: AsyncSession, wastage_inventory: WastageInventoryCreate) ->  WastageInventory:
        """Create a new WastageInventory entry.
        This method will receive an AssignmentInventoryCreate schema instance
        and return a created WastageInventory instance.
        """
        pass    
    
        
    async def list_added_assigned_inventory(self, db: AsyncSession, skip: int = 0) -> List[WastageInventoryRedisOut]:
        """
        Retrieve all AssignmentInventory entries.
        This method will return a list of AssignmentInventoryOut schema instances.
        """
        pass


    async def search_entries_by_employee_name(self, db: AsyncSession, search_filter: WastageInventorySearch) -> List[WastageInventoryRedisOut]:
        """
        Search all entries in local Redis by employee_name.
        Returns a list of AssignmentInventoryRedisOut schema instances.
        """
        pass
    
    # Edit/Update exesting AssignmentInventory directly in local Redis
    async def update_assignment_inventory_in_redis(
        self, 
        db: AsyncSession,
        assignment_inventory: WastageInventoryUpdate
    ) -> Optional[WastageInventoryRedisOut]:
        """Update an existing WastageInventory entry.
        This function protects immutable fields (uuid, sno, inventory_id, product_id, created_at)
        and ensures that they cannot be modified.
        Args:
            assignment_inventory (WastageInventoryUpdate): The data used to update the WastageInventory.
        Returns:
            Optional[WastageInventoryRedisOut]: The updated WastageInventory data after the modification,or None if the update fails or no changes were made.
        """
        pass

    async def get_by_employee_name(self, db: AsyncSession, employee_name: str) -> Optional[WastageInventoryRedisOut]:
        """Get WastageInventory entry by its employee_name (not UUID).
        Returns single WastageInventoryRedisOut instance or None if not found.
        """
        pass

    # ------------------------------------------------------------------------------------------------
    async def delete_assigned_inventory(
        self,
        db: AsyncSession,
        employee_name: str,
        update_data: WastageInventoryUpdate
    ) -> Optional[WastageInventoryRedisOut]:
        pass