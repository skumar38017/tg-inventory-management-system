#  backend/utils/inventory_updater.py

# backend/app/utils/inventory_updater.py
from typing import Dict, Any
from app.database.redisclient import redis_client

class InventoryUpdater:
    @staticmethod
    def _get_inventory_key(inventory_id: str) -> str:
        return f"inventory:{inventory_id}"

    @staticmethod
    def _update_redis_inventory(inventory_id: str, updates: Dict[str, Any]):
        key = InventoryUpdater._get_inventory_key(inventory_id)
        with redis_client.pipeline() as pipe:
            pipe.hmset(key, updates)
            pipe.execute()

    @staticmethod
    def _get_current_inventory(inventory_id: str) -> Dict[str, Any]:
        key = InventoryUpdater._get_inventory_key(inventory_id)
        return redis_client.hgetall(key)

    @staticmethod
    def update_inventory(
        inventory_id: str,
        total_qty: float = 0,
        issue_qty: float = 0,
        operation: str = None
    ) -> Dict[str, Any]:
        """
        Update inventory quantities in Redis based on the operation.
        
        Args:
            inventory_id: ID of the inventory to update
            total_qty: Quantity to add to Total Qty (default 0)
            issue_qty: Quantity to add to Issue Qty (default 0)
            operation: Name of the operation for logging (optional)
            
        Returns:
            Updated inventory data
        """
        current = InventoryUpdater._get_current_inventory(inventory_id)
        
        if not current:
            raise ValueError(f"Inventory with ID {inventory_id} not found in Redis")
            
        # Convert Redis bytes to float if needed
        current_total = float(current.get(b'Total Qty', 0) if isinstance(current.get(b'Total Qty'), bytes) else current.get('Total Qty', 0))
        current_issue = float(current.get(b'Issue Qty', 0) if isinstance(current.get(b'Issue Qty'), bytes) else current.get('Issue Qty', 0))
        
        # Calculate new values
        new_total = current_total + total_qty
        new_issue = current_issue + issue_qty
        new_balance = new_total - new_issue
        
        updates = {
            'Total Qty': new_total,
            'Issue Qty': new_issue,
            'Balance Qty': new_balance
        }
        
        InventoryUpdater._update_redis_inventory(inventory_id, updates)
        return updates

    @staticmethod
    def handle_to_event(total_qty: float, inventory_id: str):
        """Handle To Event operation - increases Issue Qty by total_qty"""
        return InventoryUpdater.update_inventory(
            inventory_id=inventory_id,
            issue_qty=total_qty,
            operation="To Event"
        )

    @staticmethod
    def handle_from_event(rec_qty: float, inventory_id: str):
        """Handle From Event operation - increases Total Qty by rec_qty"""
        return InventoryUpdater.update_inventory(
            inventory_id=inventory_id,
            total_qty=rec_qty,
            operation="From Event"
        )

    @staticmethod
    def handle_assign_inventory(qty: float, rec_qty: float, inventory_id: str):
        """Handle Assign Inventory operation - increases both Issue Qty and Total Qty"""
        return InventoryUpdater.update_inventory(
            inventory_id=inventory_id,
            total_qty=rec_qty,
            issue_qty=qty,
            operation="Assign Inventory"
        )

    @staticmethod
    def handle_damage(qty: float, inventory_id: str):
        """Handle Damage operation - increases Issue Qty by qty"""
        return InventoryUpdater.update_inventory(
            inventory_id=inventory_id,
            issue_qty=qty,
            operation="Damage"
        )