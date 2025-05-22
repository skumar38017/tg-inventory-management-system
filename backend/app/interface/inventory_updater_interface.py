#  backend/app/interface/inventory_updater.py
from typing import Dict, Any
from backend.app.schema.entry_inventory_schema import InventoryRedisOut

class InventoryUpdaterInterface:
    """Interface for InventoryUpdater"""
    async def update_inventory(
        self,
        inventory_name: str,
        total_quantity: int = 0,
        issued_qty: int = 0,
        operation: str = None
    ) -> InventoryRedisOut:
        """Update inventory quantities in Redis based on the operation.
        
        Args:
            inventory_name: ID of the inventory to update
            inventory_id: ID of the inventory to update
            
        Returns:
            Updated inventory data as InventoryRedisOut
            
        Raises:
            ValueError: If inventory is not found in Redis
        """
        pass
    
    async def handle_to_event(self, data: dict) -> InventoryRedisOut:
        """Handle To Event operation - increases Issue Qty by total
        
        Args:
            data: Dictionary containing:
                - name: ID of the inventory to update
                - total: Quantity to add to issued quantity
            
        Returns:
            Updated inventory data
        """
        pass

    async def handle_from_event(self, data: dict) -> InventoryRedisOut:
        """Handle From Event operation - increases Total Qty by rec_qty
        
        Args:
            data: Dictionary containing:                
                - name: ID of the inventory to update
                - RecQty: Quantity to add to total quantity
            
        Returns:
            Updated inventory data
        """
        pass
    
    async def handle_assign_inventory(self, rec_qty: int, quantity: int, inventory_name: str) -> InventoryRedisOut:
        """Handle Assign Inventory operation - increases both Issue Qty and Total Qty
        
        Args:
            rec_qty: Quantity to add to total quantity
            quantity: Quantity to add to issued quantity
            inventory_name: ID of the inventory to update
            
        Returns:
            Updated inventory data
        """
        pass

    async def handle_damage(self, quantity: int, inventory_name: str) -> InventoryRedisOut:
        """Handle Damage operation - increases Issue Qty by quantity
        
        Args:
            quantity: Quantity to add to issued quantity
            inventory_name: ID of the inventory to update
            
        Returns:
            Updated inventory data
        """
        pass

    async def create_inventory(self, inventory_data: Dict[str, Any]) -> InventoryRedisOut:
        """
        Create a new inventory record in Redis
        
        Args:
            inventory_data: Dictionary containing inventory data including 'inventory_name'
            
        Returns:
            Created inventory data as InventoryRedisOut
            
        Raises:
            ValueError: If inventory_name is not provided
        """ 
        pass

    async def handle_update_entry(self, data: dict) -> InventoryRedisOut:
        """Update an existing inventory entry with new quantity values"""   
        pass