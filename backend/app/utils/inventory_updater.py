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
        operation: str = None
    ) -> InventoryRedisOut:
        """
        Update inventory quantities in Redis based on the operation.
        
        Args:
            inventory_name: ID of the inventory to update
            total_quantity: Quantity to add to Total Qty (default 0)
            issued_qty: Quantity to add to Issue Qty (default 0)
            operation: Name of the operation for logging (optional)
            
        Returns:
            Updated inventory data as InventoryRedisOut
            
        Raises:
            ValueError: If inventory is not found in Redis
        """
        current = await self._get_current_inventory(inventory_name)
        
        if not current:
            raise ValueError(f"Inventory with ID {inventory_name} not found in Redis")
            
        current_total = int(current.get('total_quantity', 0))
        current_issue = int(current.get('issued_qty', 0))
        
        new_total = current_total + total_quantity
        new_issue = current_issue + issued_qty
        new_balance = new_total - new_issue
        
        updates = current.copy()
        updates.update({
            'total_quantity': new_total,
            'issued_qty': new_issue,
            'balance_qty': new_balance
        })
        
        await self._update_redis_inventory(inventory_name, updates)
        return InventoryRedisOut(**updates)
            
    async def handle_to_event(self, data: dict) -> InventoryRedisOut:
        try:
            if not data.get('name'):
                raise ValueError("Inventory name is required")
            if 'total' not in data:
                raise ValueError("Total quantity is required")
                
            # If inventory_id is not provided, search by name
            if not data.get('inventory_id'):
                # Get all inventory keys
                keys = await self.redis.keys("inventory:*")
                
                # Find matching inventory by name
                matching_key = None
                for key in keys:
                    # Extract inventory_name from key (format: "inventory:{name}{id}")
                    key_parts = key.split(':')
                    if len(key_parts) != 2:
                        continue
                        
                    # The full identifier is the part after "inventory:"
                    full_identifier = key_parts[1]
                    
                    # Try to find where the name ends and ID begins
                    # We know inventory_name is at the start and ID is at the end
                    # So we'll check if the name matches the beginning of the identifier
                    inventory_name = data['name']
                    if full_identifier.startswith(inventory_name):
                        matching_key = key
                        break
                
                if not matching_key:
                    raise ValueError(f"Inventory with name {data['name']} not found in Redis")
                    
                # Extract the inventory_id from the matching key
                # The ID is whatever comes after the inventory_name in the key
                inventory_id = full_identifier[len(inventory_name):]
                data['inventory_id'] = inventory_id
            else:
                # If inventory_id was provided, use it directly
                matching_key = f"inventory:{data['name']}{data['inventory_id']}"
                
            # Verify the inventory exists
            exists = await self.redis.exists(matching_key)
            if not exists:
                raise ValueError(f"Inventory {data['name']} with ID {data.get('inventory_id')} not found in Redis")
        
            logger.info(f"Processing To Event for inventory: {data['name']}")
            result = await self.update_inventory(
                inventory_name=data['name'],
                issued_qty=data['total'],
                operation="To Event"
            )
            logger.info(f"Successfully updated inventory: {data['name']}")
            return result
        except Exception as e:
            logger.error(f"Failed to process To Event for {data.get('name')}: {str(e)}")
            raise

    async def handle_from_event(self, data: dict) -> InventoryRedisOut:
        """Handle From Event operation"""
        return await self.update_inventory(
            inventory_name=data['name'],
            total_quantity=data['RecQty'],  
            operation="From Event" 
        )
    
    async def handle_assign_inventory(
        self, 
        rec_qty: int, 
        quantity: int, 
        inventory_name: str
    ) -> InventoryRedisOut:
        """Handle Assign Inventory operation"""
        return await self.update_inventory(
            inventory_name=inventory_name,
            total_quantity=rec_qty,
            issued_qty=quantity,
            operation="Assign Inventory"
        )

    async def handle_damage(self, quantity: int, inventory_name: str) -> InventoryRedisOut:
        """Handle Damage operation"""
        return await self.update_inventory(
            inventory_name=inventory_name,
            issued_qty=quantity,
            operation="Damage"
        )

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