# backend/app/services/qrcode_service.py

from typing import Optional, Dict, Any
from backend.app.database.redisclient import get_redis_dependency
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
from backend.app.schema.qrcode_barcode_schema import InventoryQrCodeResponse
import logging
import json
from sqlalchemy import select, delete
import redis.asyncio as redis
from backend.app import config

logger = logging.getLogger(__name__)

class QRCodeService:
    def __init__(self, redis_client: aioredis.Redis):
        # QR Code Configuration
        self.redis = redis_client
        self.base_url = config.BASE_URL
        self.qrcode_base_path = config.QRCODE_BASE_PATH
        self.qrcode_base_url = config.QRCODE_BASE_URL
        self.public_api_url = config.PUBLIC_API_URL


    async def get_inventory_item_by_qr(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """
        Fetch inventory item by QR code data from Redis only
        Supports multiple lookup methods in Redis:
        1. Direct key match
        2. Pattern matching with inventory prefix
        3. Wildcard search
        """
        try:
            return await self._fetch_from_redis(qr_data)
        except Exception as e:
            logger.error(f"Failed to fetch inventory item from Redis: {str(e)}")
            raise
    
    async def _fetch_from_redis(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """Check Redis for inventory data using multiple possible keys"""
        # Try these lookup methods in order
        lookup_methods = [
            self._direct_redis_lookup,
            self._prefixed_redis_lookup,
            self._wildcard_redis_lookup
        ]
        
        for method in lookup_methods:
            item = await method(qr_data)
            if item:
                return item
                
        return None
    
    async def _direct_redis_lookup(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """Check for exact key match"""
        try:
            item_data = await self.redis.get(qr_data)  # Added await here
            if item_data:
                return self._parse_redis_item(item_data)
        except Exception as e:
            logger.warning(f"Direct Redis lookup failed: {str(e)}")
        return None
    
    async def _prefixed_redis_lookup(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """Check for keys with inventory: prefix"""
        try:
            redis_key = f"inventory:{qr_data}"
            item_data = await self.redis.get(redis_key) 
            if item_data:
                return self._parse_redis_item(item_data)
        except Exception as e:
            logger.warning(f"Prefixed Redis lookup failed: {str(e)}")
        return None
    
    async def _wildcard_redis_lookup(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """Scan Redis for keys containing the qr_data"""
        try:
            # Search with inventory: prefix first
            pattern = f"inventory:*{qr_data}*"
            keys = []
            cursor = "0"  # Start with initial cursor
            
            # First scan for keys
            while True:
                cursor, partial_keys = await self.redis.scan(  # Added await here
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                keys.extend(partial_keys)
                if cursor == "0":  # Done when cursor returns to "0"
                    break
            
            # Check each found key
            for key in keys:
                item_data = await self.redis.get(key)  # Added await here
                if item_data:
                    item = self._parse_redis_item(item_data)
                    if item:
                        return item
                        
            # Fall back to non-prefixed search if nothing found
            pattern = f"*{qr_data}*"
            keys = []
            cursor = "0"
            
            while True:
                cursor, partial_keys = await self.redis.scan(  # Added await here
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                keys.extend(partial_keys)
                if cursor == "0":
                    break
            
            for key in keys:
                item_data = await self.redis.get(key)  # Added await here
                if item_data:
                    item = self._parse_redis_item(item_data)
                    if item:
                        return item
                        
        except Exception as e:
            logger.warning(f"Wildcard Redis lookup failed: {str(e)}")
            
        return None
    
    def _parse_redis_item(self, item_data: str) -> Optional[Dict[str, Any]]:
        """Parse Redis item data and validate structure"""
        try:
            item = json.loads(item_data)
            # Basic validation that this is an inventory item
            if isinstance(item, dict) and ('inventory_id' in item or 'inventory_name' in item):
                return item
            return None
        except json.JSONDecodeError:
            return None
    
    def map_to_response_schema(self, item_data: Dict[str, Any]) -> InventoryQrCodeResponse:
        """Map raw inventory data to our response schema"""
        # Map all fields that exist in both the model and schema
        mapped_data = {
            "company": "Tagglabs Experiential PVT. LTD.",
            "type": "inventory",
            **{k: v for k, v in item_data.items() 
               if k in InventoryQrCodeResponse.model_fields}
        }
        
        # Handle special cases
        date_fields = ['purchase_date', 'created_at', 'updated_at']
        for field in date_fields:
            if field in item_data and item_data[field]:
                if isinstance(item_data[field], str):
                    mapped_data[field] = item_data[field]
                else:
                    mapped_data[field] = item_data[field].isoformat()
        
        return InventoryQrCodeResponse(**mapped_data)