import redis
import pandas as pd
from typing import Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)

class IDVerification:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    def is_duplicate(self, inventory_name: str, inventory_id: str) -> bool:
        """Check if inventory already exists in Redis"""
        redis_key = f"inventory:{inventory_name}{inventory_id}"
        return self.redis_client.exists(redis_key)
    
    def validate_batch_data(self, data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """Check batch data for existing entries in Redis"""
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Check which entries already exist in Redis
        existing_entries = []
        valid_entries = []
        
        for _, row in df.iterrows():
            if self.is_duplicate(row['inventory_name'], row['inventory_id']):
                existing_entries.append(row.to_dict())
            else:
                valid_entries.append(row.to_dict())
        
        return {
            "valid_entries": valid_entries,
            "duplicates": existing_entries,
            "total_valid": len(valid_entries),
            "total_duplicates": len(existing_entries)
        }
    
    def safe_store_check(self, data: Union[Dict, List[Dict]]) -> Dict[str, Any]:
        """Check data before storage - returns validation result only"""
        if isinstance(data, dict):
            data = [data]
        
        validation_result = self.validate_batch_data(data)
        
        return {
            "can_store": validation_result["total_valid"] > 0,
            "valid_entries": validation_result["valid_entries"],
            "duplicates": validation_result["duplicates"],
            "message": f"Found {validation_result['total_valid']} valid, {validation_result['total_duplicates']} duplicates"
        }
