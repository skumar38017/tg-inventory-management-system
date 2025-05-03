# backend/app/services/qrcode_service.py

from typing import Optional, Dict, Any
from backend.app.database.redisclient import get_redis_dependency
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
from backend.app.schema.qrcode_barcode_schema import InventoryQrCodeResponse
import logging
import json
import re
from sqlalchemy import select, delete
import redis.asyncio as redis
from backend.app import config
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class QRCodeService:
    def __init__(self, redis_client: aioredis.Redis):
        # QR Code Configuration
        self.redis = redis_client
        self.base_url = config.BASE_URL
        self.qrcode_base_path = config.QRCODE_BASE_PATH
        self.qrcode_base_url = config.QRCODE_BASE_URL
        self.public_api_urls = config.PUBLIC_API_URLS
        self.public_api_url = config.PUBLIC_API_URL.rstrip('/')
        self.scan_endpoint = f"{self.public_api_url}/api/v1/scan/"


    def _extract_inventory_id(self, input_str: str) -> Optional[str]:
        """Extract inventory ID from string using common patterns"""
        patterns = [
            r'(INV\d+)',          # Standard format (INV001)
            r'(PRD\d+)',          # Product ID format (PRD001)
            r'([A-Z]{3}\d{3,})',  # Three letters + numbers (ABC123)
            r'(\d{4,})'           # Pure numbers (0001, 1001)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, input_str)
            if match:
                return match.group(1)
        return None

    def _extract_qr_data_from_url(self, url: str) -> Optional[str]:
            """
            Extract the inventory identifier from a QR code URL
            Handles formats like:
            - https://rwf1rlkq-8000.inc1.devtunnels.ms/api/v1/scan/SteelRodINV003
            - http://localhost:8000/api/v1/scan/INV003
            - Handles multiple possible public URLs
            """
            try:
                parsed = urlparse(url)
                
                # Check against all possible public API URLs
                for api_url in self.public_api_urls:
                    api_parsed = urlparse(api_url)
                    
                    # Check if path starts with scan endpoint
                    if parsed.path.startswith('/api/v1/scan/'):
                        return parsed.path.split('/api/v1/scan/')[-1]
                    
                    # Match same netloc (domain) if full URL provided
                    if parsed.netloc == api_parsed.netloc and '/api/v1/scan/' in parsed.path:
                        return parsed.path.split('/api/v1/scan/')[-1]
                
                return None
            except Exception as e:
                logger.warning(f"Failed to parse URL {url}: {str(e)}")
                return None


         # backend/app/services/qrcode_service.py

    def _standardize_qr_input(self, qr_data: str) -> str:
        """Convert various QR code formats to standard inventory:name|id format"""
        # If already in standard format
        if qr_data.startswith("inventory:") and "|" in qr_data:
            return qr_data
        
        # Handle pipe-separated formats
        if "|" in qr_data:
            parts = qr_data.split("|")
            if len(parts) == 2:
                return f"inventory:{parts[0]}|{parts[1]}"
        
        # Handle combined name+ID format (e.g., "LED Stage LightINV45678")
        inventory_id = self._extract_inventory_id(qr_data)
        if inventory_id:
            name_part = qr_data.replace(inventory_id, "")
            return f"inventory:{name_part}|{inventory_id}"
        
        # Fallback - try to use as-is
        return qr_data
       
    async def get_inventory_item_by_qr(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """
        Enhanced lookup that handles:
        - Full name+ID (Steel RodINV002)
        - Just ID (INV002)
        - QR code content (name+ID|ID)
        - Full API URLs (https://.../api/v1/scan/SteelRodINV003)
        """
        try:
            # First check if this is a URL from our public API
            if qr_data.startswith(('http://', 'https://')):
                extracted_data = self._extract_qr_data_from_url(qr_data)
                if extracted_data:
                    qr_data = extracted_data
                else:
                    logger.warning(f"Could not extract data from URL: {qr_data}")

            # First try direct lookup
            item = await self._direct_redis_lookup(qr_data)
            if item:
                return item

            # Handle pipe-separated QR content (name+ID|ID)
            if '|' in qr_data:
                for part in qr_data.split('|'):
                    item = await self._direct_redis_lookup(part.strip())
                    if item:
                        return item

            # Try extracting inventory ID
            inventory_id = self._extract_inventory_id(qr_data)
            if inventory_id:
                # Check ID index first
                redis_key = await self.redis.get(f"inventory:id:{inventory_id}")
                if redis_key:
                    item_data = await self.redis.get(redis_key)
                    if item_data:
                        return self._parse_redis_item(item_data)
                
                # Fallback to wildcard search
                pattern = f"*{inventory_id}*"
                cursor = "0"
                while True:
                    cursor, keys = await self.redis.scan(
                        cursor=cursor,
                        match=pattern,
                        count=100
                    )
                    for key in keys:
                        item_data = await self.redis.get(key)
                        if item_data:
                            return self._parse_redis_item(item_data)
                    if cursor == "0":
                        break

            return None
        except Exception as e:
            logger.error(f"Lookup failed: {str(e)}")
            raise

    async def _fetch_from_redis(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """Check Redis for inventory data using multiple possible keys"""
        # Handle URL-formatted QR codes first
        if qr_data.startswith(('http://', 'https://')):
            extracted_data = self._extract_qr_data_from_url(qr_data)
            if extracted_data:
                qr_data = extracted_data
            else:
                logger.warning(f"Could not extract data from URL: {qr_data}")
                return None
                
        # First try direct key match
        item = await self._direct_redis_lookup(qr_data)
        if item:
            return item
            
        # Try with inventory: prefix if not already present
        if not qr_data.startswith('inventory:'):
            qr_data = f"inventory:{qr_data}"
        
        # Try again with the processed data
        return await self._direct_redis_lookup(qr_data)
    
    async def _direct_redis_lookup(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """Check for exact key match"""
        try:
            item_data = await self.redis.get(qr_data)
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