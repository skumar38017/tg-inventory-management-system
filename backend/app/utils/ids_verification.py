import redis.asyncio as aioredis
import pandas as pd
from typing import Dict, Any, List, Union
import logging
import json

logger = logging.getLogger(__name__)

class IDVerification:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
    
    async def is_duplicate(self, inventory_name: str, inventory_id: str, product_id: str = None) -> tuple[bool, str]:
        """Check if inventory already exists in Redis - returns (is_duplicate, message)"""
        # Check inventory_name + inventory_id combination
        redis_key = f"inventory:{inventory_name}{inventory_id}"
        if await self.redis_client.exists(redis_key):
            return True, f"Inventory combination already exists: {inventory_name} - {inventory_id}"
        
        # Check if product_id or inventory_id exists individually in any record
        if product_id:
            pattern = "inventory:*"
            async for key in self.redis_client.scan_iter(match=pattern):
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        inventory_data = json.loads(data)
                        
                        # Check if product_id already exists
                        if inventory_data.get("product_id") == product_id:
                            return True, f"Product ID already exists: {product_id}"
                        
                        # Check if inventory_id already exists
                        if inventory_data.get("inventory_id") == inventory_id:
                            return True, f"Inventory ID already exists: {inventory_id}"
                except:
                    continue
        
        return False, "No duplicates found"
    
    async def validate_batch_data(self, data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """Check batch data for existing entries in Redis"""
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Check which entries already exist in Redis
        existing_entries = []
        valid_entries = []
        
        for _, row in df.iterrows():
            is_dup, message = await self.is_duplicate(row['inventory_name'], row['inventory_id'], row.get('product_id'))
            if is_dup:
                existing_entries.append(row.to_dict())
            else:
                valid_entries.append(row.to_dict())
        
        return {
            "valid_entries": valid_entries,
            "duplicates": existing_entries,
            "total_valid": len(valid_entries),
            "total_duplicates": len(existing_entries)
        }
    
    async def safe_store_check(self, data: Union[Dict, List[Dict]]) -> Dict[str, Any]:
        """Check data before storage - returns validation result only"""
        if isinstance(data, dict):
            data = [data]
        
        validation_result = await self.validate_batch_data(data)
        
        return {
            "can_store": validation_result["total_valid"] > 0,
            "valid_entries": validation_result["valid_entries"],
            "duplicates": validation_result["duplicates"],
            "message": f"Found {validation_result['total_valid']} valid, {validation_result['total_duplicates']} duplicates"
        }
