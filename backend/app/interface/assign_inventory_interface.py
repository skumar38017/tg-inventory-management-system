#  backend/app/interface/assign_inventory_interface.py
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import List, Optional
from app.models.assign_inventory_model import AssignmentInventory
from app.schema.assign_inventory_schema import (
    AssignmentInventoryCreate,
    AssignmentInventoryUpdate,
    AssignmentInventoryRedisOut,
    AssignmentInventorySearch,
)
from pydantic import BaseModel
from datetime import date

class AssignmentInventoryInterface:
    """Interface for AssignmentInventory operations with immutable core fields."""
    
    # # Upload all `assignment_inventory` entries from local Redis to the database after click on `upload data` button
    async def upload_assignment_inventory(self, db: AsyncSession, skip: int = 0) -> List[AssignmentInventoryRedisOut]:
        """
        Upload all `assignment_inventory` entries from local Redis to the database.
        Returns a list of AssignmentInventoryRedisOut schema instances.
        """
        raise NotImplementedError
   
   
    async def create_assignment_inventory(self, db: AsyncSession, assignment_inventory: AssignmentInventoryCreate) -> AssignmentInventory:
        """
        Create a new AssignmentInventory entry.
        This method will receive an AssignmentInventoryCreate schema instance
        and return a created AssignmentInventory instance.
        """
        pass    
    
        
    async def list_added_assigned_inventory(self, db: AsyncSession, skip: int = 0) -> List[AssignmentInventoryRedisOut]:
        """
        Retrieve all AssignmentInventory entries.
        This method will return a list of AssignmentInventoryOut schema instances.
        """
        pass


    async def search_entries_by_employee_name(self, db: AsyncSession, search_filter: AssignmentInventorySearch) -> List[AssignmentInventoryRedisOut]:
        """
        Search all entries in local Redis by employee_name.
        Returns a list of AssignmentInventoryRedisOut schema instances.
        """
        pass
    
    # Edit/Update exesting AssignmentInventory directly in local Redis
    async def update_assignment_inventory_in_redis(
        self, 
        db: AsyncSession,
        assignment_inventory: AssignmentInventoryUpdate
    ) -> Optional[AssignmentInventoryRedisOut]:
        """
        Update an existing AssignmentInventory entry.
        
        This function protects immutable fields (uuid, sno, inventory_id, product_id, created_at)
        and ensures that they cannot be modified.
        
        Args:
            assignment_inventory (AssignmentInventoryUpdate): The data used to update the AssignmentInventory.
        
        Returns:
            Optional[AssignmentInventoryRedisOut]: The updated AssignmentInventory data after the modification,
                                        or None if the update fails or no changes were made.
        """
        # Logic for updating the AssignmentInventory in Redis would go here.
        # This might involve fetching the current AssignmentInventory data,
        # applying changes while protecting immutable fields,
        # and then saving the updated data back into Redis.
        
        pass

    async def get_by_employee_name(self, db: AsyncSession, employee_name: str) -> Optional[AssignmentInventoryRedisOut]:
        """
        Get AssignmentInventory entry by its employee_name (not UUID).
        Returns single AssignmentInventoryRedisOut instance or None if not found.
        """
        pass

    # ------------------------------------------------------------------------------------------------
    async def delete_assigned_inventory(
        self,
        db: AsyncSession,
        employee_name: str,
        update_data: AssignmentInventoryUpdate
    ) -> Optional[AssignmentInventoryRedisOut]:
        pass