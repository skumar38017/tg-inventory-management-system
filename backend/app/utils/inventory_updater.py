# backend/app/utils/inventory_updater.py
from typing import Dict, Any
from backend.app.database.redisclient import get_redis_dependency
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
from backend.app import config
from backend.app.schema.entry_inventory_schema import StoreInventoryRedis, InventoryRedisOut
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class InventoryUpdater:
    """Implementation of EntryInventoryInterface with async operations"""
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.base_url = config.BASE_URL
    
    async def update_inventory_by_id(self, inventory_name: str, inventory_id: str):
        """Check if inventory exists by ID"""
        redis_key = await self._get_inventory_key(inventory_name, inventory_id)
        inventory_data = await self.redis.get(redis_key)
        if not inventory_data:
            raise ValueError(f"Inventory with ID {inventory_name} not found in Redis")

    async def _get_inventory_key(self, inventory_name: str, inventory_id: str = None) -> str:
        """More flexible version that can handle both cases"""
        if inventory_id:
            return f"inventory:{inventory_name}{inventory_id}"
        # Try to find by name only (may need to scan keys)
        pattern = f"inventory:{inventory_name}*"
        keys = await self.redis.keys(pattern)
        if not keys:
            raise ValueError(f"No inventory found matching {inventory_name}")
        if len(keys) > 1:
            raise ValueError(f"Multiple inventories match {inventory_name}")
        return keys[0]

    async def _update_redis_inventory(self, inventory_name: str, inventory_data: Dict[str, Any]):
        """Update inventory data in Redis"""
        key = await self._get_inventory_key(inventory_name)
        inventory = StoreInventoryRedis(**inventory_data)
        await self.redis.set(key, inventory.model_dump_json())

    async def _get_current_inventory(self, inventory_name: str) -> Dict[str, Any]:
        """Get current inventory data from Redis"""
        key = await self._get_inventory_key(inventory_name)
        logger.debug(f"Attempting to get inventory with key: {key}")
        inventory_json = await self.redis.get(key)
        
        if not inventory_json:
            logger.warning(f"No inventory found with key: {key}")
            return {}
            
        return json.loads(inventory_json)

    async def update_inventory(
        self,
        inventory_name: str,
        total_quantity: int = 0,
        issued_qty: int = 0,
        operation: str = None,
        adjustment_mode: bool = False  # New flag for update operations
    ) -> InventoryRedisOut:
        """
        Update inventory quantities in Redis with enhanced handling for updates.
        
        Args:
            inventory_name: Name/ID of the inventory to update
            total_quantity: Quantity to add/set for Total Qty (default 0)
            issued_qty: Quantity to add/set for Issue Qty (default 0)
            operation: Name of the operation for logging (optional)
            adjustment_mode: If True, treats quantities as adjustments (add/subtract)
                        If False, treats quantities as absolute values (set)
                        
        Returns:
            Updated inventory data as InventoryRedisOut
            
        Raises:
            ValueError: If inventory is not found in Redis
            ValueError: If trying to set negative quantities
        """
        current = await self._get_current_inventory(inventory_name)
        
        if not current:
            raise ValueError(f"Inventory {inventory_name} not found in Redis")
            
        # Get current values with proper type conversion
        current_total = int(current.get('total_quantity', 0))
        current_issue = int(current.get('issued_qty', 0))
        
        # Calculate new values based on adjustment mode
        if adjustment_mode:
            # For adjustments (during project updates)
            new_total = current_total + total_quantity
            new_issue = current_issue + issued_qty
        else:
            # For absolute values (during project creation)
            new_total = total_quantity if total_quantity != 0 else current_total
            new_issue = issued_qty if issued_qty != 0 else current_issue
        
        # Validate quantities won't go negative
        if new_total < 0 or new_issue < 0 or (new_total - new_issue) < 0:
            raise ValueError(
                f"Invalid quantities would result in negative values: "
                f"Total={new_total}, Issued={new_issue}, Balance={new_total - new_issue}"
            )
        
        # Prepare updates
        updates = current.copy()
        updates.update({
            'total_quantity': new_total,
            'issued_qty': new_issue,
            'balance_qty': new_total - new_issue,
        })
        
        # Apply updates
        await self._update_redis_inventory(inventory_name, updates)
        
        logger.info(
            f"Inventory {inventory_name} updated: "
            f"Total {current_total}→{new_total}, "
            f"Issued {current_issue}→{new_issue}, "
            f"Operation: {operation or 'N/A'}"
        )
        
        return InventoryRedisOut(**updates)

    async def handle_to_event(self, data: dict) -> InventoryRedisOut:
        try:
            if not data.get('name'):
                raise ValueError("Inventory name is required")
            if 'total' not in data:
                raise ValueError("Total quantity is required")
                
            # Determine if this is an adjustment (update) or absolute (create)docker 
            is_adjustment = data.get('is_adjustment', False)
            
            # If inventory_id is not provided, search by name
            if not data.get('inventory_id'):
                keys = await self.redis.keys("inventory:*")
                matching_key = None
                for key in keys:
                    key_parts = key.split(':')
                    if len(key_parts) == 2 and key_parts[1].startswith(data['name']):
                        matching_key = key
                        break
                
                if not matching_key:
                    raise ValueError(f"Inventory {data['name']} not found")
                    
                data['inventory_id'] = key_parts[1][len(data['name']):]
            
            logger.info(f"Processing To Event for inventory: {data['name']}")
            
            result = await self.update_inventory(
                inventory_name=data['name'],
                issued_qty=data['total'],
                operation="To Event",
                adjustment_mode=is_adjustment
            )
            
            logger.info(f"Successfully updated inventory: {data['name']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process To Event for {data.get('name')}: {str(e)}")
            raise
       
    async def handle_from_event(self, data: dict) -> InventoryRedisOut:
        try:
            if not data.get('name'):
                raise ValueError("Inventory name is required")
            if 'RecQty' not in data:
                raise ValueError("Received quantity (RecQty) is required")

            # Convert RecQty to integer
            rec_qty = int(data['RecQty'])
            if rec_qty <= 0:
                raise ValueError("RecQty must be positive")

            # Default to adjustment mode for returns
            is_adjustment = data.get('is_adjustment', True)

            # Find inventory by name if ID not provided
            if not data.get('inventory_id'):
                keys = await self.redis.keys("inventory:*")
                matching_key = None
                for key in keys:
                    key_parts = key.split(':')
                    if len(key_parts) == 2 and key_parts[1].startswith(data['name']):
                        matching_key = key
                        break
                
                if not matching_key:
                    raise ValueError(f"Inventory {data['name']} not found")
                    
                data['inventory_id'] = key_parts[1][len(data['name']):]

            logger.info(f"Processing return for {data['name']} (Qty: {rec_qty})")

            # For returns, we:
            # 1. Decrease issued_qty by RecQty
            # 2. Balance auto-updates via (total_quantity - issued_qty)
            result = await self.update_inventory(
                inventory_name=data['name'],
                issued_qty=-rec_qty,  # Negative to decrease issued quantity
                operation="From Event",
                adjustment_mode=is_adjustment
            )

            logger.info(
                f"Successfully processed return - {data['name']}: "
                f"Issued reduced by {rec_qty}, "
                f"New balance: {result.balance_qty}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to process return for {data.get('name')}: {str(e)}")
            raise

    async def handle_assign_inventory(self, data: dict) -> InventoryRedisOut:
        try:
            # Validate required fields
            if not data.get('name'):
                raise ValueError("Inventory name is required")
            if 'quantity' not in data:
                raise ValueError("Quantity is required")
            # Convert quantity to integer
            try:
                quantity = int(data['quantity'])
            except (ValueError, TypeError):
                raise ValueError("Quantity must be a valid number")

            logger.info(f"Processing assignment update for {data['name']} (Qty: {quantity})")

            # Update inventory - adjust issued quantity (can be positive or negative)
            result = await self.update_inventory(
                inventory_name=data['name'],
                issued_qty=quantity,  # Can be positive or negative
                operation="Assignment Update",
                adjustment_mode=True  # Treat as adjustment
            )

            logger.info(
                f"Successfully processed assignment update - {data['name']}: "
                f"Issued {'increased' if quantity > 0 else 'decreased'} by {abs(quantity)}, "
                f"New balance: {result.balance_qty}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to process assignment update for {data.get('name')}: {str(e)}")
            raise

    async def handle_wastage(self, data: dict) -> InventoryRedisOut:
        """Handle Wastage operation (for returned/approved items)"""
        try:
            if not data.get('name'):
                raise ValueError("Inventory name is required")
            if 'quantity' not in data:
                raise ValueError("Quantity is required")
            
            # Convert quantity to integer
            try:
                quantity = int(data['quantity'])
            except (ValueError, TypeError):
                raise ValueError("Quantity must be a valid number")

            if quantity <= 0:
                raise ValueError("Quantity must be positive")

            # Get current inventory state
            current = await self._get_current_inventory(data['name'])
            if not current:
                raise ValueError(f"Inventory {data['name']} not found")
                
            current_total = int(current.get('total_quantity', 0))
            current_issued = int(current.get('issued_qty', 0))
            current_balance = current_total - current_issued

            # Check if wastage would make balance negative
            if (current_total - quantity) < current_issued:
                # First return all issued items before marking as wastage
                if current_issued > 0:
                    await self.update_inventory(
                        inventory_name=data['name'],
                        issued_qty=-current_issued,  # Return all issued items
                        operation="Return Before Wastage"
                    )
                
                # Verify we can now perform wastage
                current_total = int(current.get('total_quantity', 0)) - current_issued
                if (current_total - quantity) < 0:
                    raise ValueError(
                        f"Cannot mark {quantity} as wastage. Only {current_total} items available after returns"
                    )

            logger.info(f"Processing wastage for {data['name']} (Qty: {quantity})")

            # Update inventory - decrease total quantity
            result = await self.update_inventory(
                inventory_name=data['name'],
                total_quantity=quantity,  # Negative to decrease total
                operation="Wastage"
            )

            logger.info(
                f"Successfully processed wastage - {data['name']}: "
                f"Total reduced by {quantity}, "
                f"New balance: {result.balance_qty}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to process wastage for {data.get('name')}: {str(e)}")
            raise


    async def create_inventory(self, inventory_data: Dict[str, Any]) -> InventoryRedisOut:
        """Create new inventory record in Redis"""
        if not inventory_data.get('inventory_name'):
            raise ValueError("Inventory ID is required")
            
        inventory_data.setdefault('total_quantity', 0)
        inventory_data.setdefault('issued_qty', 0)
        inventory_data.setdefault('balance_qty', 0)
        
        inventory = StoreInventoryRedis(**inventory_data)
        key = await self._get_inventory_key(inventory.inventory_name)
        await self.redis.set(key, inventory.model_dump_json())
        
        return InventoryRedisOut(**inventory.model_dump())