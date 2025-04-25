import gspread
from backend.app.database.redisclient import get_redis_dependency
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
from google.oauth2.service_account import Credentials
from fastapi import HTTPException, Request
from typing import List, Optional
import json
import random
import logging
from typing import List, Optional, Dict, Any, Union
from fastapi import Request
from starlette.requests import Request as StarletteRequest

import uuid
from datetime import datetime
from pydantic import BaseModel
from backend.app.utils.date_utils import UTCDateUtils
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryBase,
    GoogleSyncInventoryCreate,
    InventoryRedisOut
)
import os
from backend.app.utils.field_validators import BaseValidators
from backend.app.interface.entry_inverntory_interface import GoogleSyncInventoryInterface
import redis.asyncio as redis
from backend.app import config
from backend.app.utils.barcode_generator import BarcodeGenerator
from google.oauth2 import service_account
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class GoogleSheetsToRedisSyncService(GoogleSyncInventoryInterface):
    """Implementation of GoogleSyncInventoryInterface with async operations"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()
        self.base_url = config.BASE_URL
        self.spreadsheet_url = config.SPREADSHEET_URL
        self.sheet_name = config.SHEET_NAME
        self.scopes = config.SCOPES
        load_dotenv()
        
        # Verify credentials file exists on initialization
        if not os.path.exists(config.SERVICE_ACCOUNT_FILE):
            logger.error(f"Google credentials file not found at: {config.SERVICE_ACCOUNT_FILE}")
            raise ValueError("Google service account credentials file not found")
        
        # Updated to match actual Google Sheet columns (10 columns)
        self.expected_headers = [
            "sno", 
            "material", 
            "total_quantity", 
            "manufacturer",
            "repair_quantity", 
            "repair_cost", 
            "issued_qty", 
            "balance_qty",
        ]

    async def _get_google_sheets_client(self):
        """Authenticate with Google Sheets API using service account"""
        try:
            creds = Credentials.from_service_account_file(
                config.SERVICE_ACCOUNT_FILE, 
                scopes=self.scopes
            )
            return gspread.authorize(creds)
            
        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to authenticate with Google Sheets"
            )

    async def _fetch_sheet_data(self):
        """Fetch data from Google Sheets"""
        try:
            gc = await self._get_google_sheets_client()
            spreadsheet = gc.open_by_url(self.spreadsheet_url)
            worksheet = spreadsheet.worksheet(self.sheet_name)
            
            # Get all values first
            all_values = worksheet.get_all_values()
            
            # Verify we have at least one row (header)
            if not all_values:
                raise HTTPException(
                    status_code=400,
                    detail="Empty worksheet - no data found"
                )
            
            # Validate headers
            actual_headers = all_values[0]
            if len(actual_headers) != len(self.expected_headers):
                logger.error(f"Header count mismatch. Expected {len(self.expected_headers)} columns, got {len(actual_headers)}")
                raise HTTPException(
                    status_code=400,
                    detail="Column count mismatch with expected headers"
                )
            
            # Log header mismatch without failing (adjust if strict matching needed)
            if actual_headers != self.expected_headers:
                logger.warning(f"Header mismatch. Expected: {self.expected_headers}, Got: {actual_headers}")
                
            # Use our expected headers to get records
            records = worksheet.get_all_records(
                expected_headers=self.expected_headers,
                head=1  # Skip header row since we're providing our own
            )
            
            logger.info(f"Fetched {len(records)} records from Google Sheets")
            return records
            
        except HTTPException:
            raise  # Re-raise our own HTTP exceptions
        except Exception as e:
            logger.error(f"Failed to fetch data from Google Sheets: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch data from Google Sheets"
            )

    def _convert_quantity(self, value):
        """Convert quantity values to integers safely"""
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return 0
        return 0

    async def _process_sheet_row(self, record: dict, idx: int) -> Optional[GoogleSyncInventoryCreate]:
        """Process a single row from Google Sheets into GoogleSyncInventoryCreate"""
        try:
            # Skip if no material name
            if not record.get('material'):
                logger.warning(f"Row {idx} skipped - no material name")
                return None

            # Convert all quantities to integers with proper defaults
            quantities = ['total_quantity', 'repair_quantity', 'issued_qty', 'balance_qty']
            for qty in quantities:
                try:
                    record[qty] = int(float(record.get(qty, 0)))
                except (ValueError, TypeError):
                    record[qty] = 0
                    logger.warning(f"Row {idx} - invalid {qty} value: {record.get(qty)}")

            # Generate IDs if not provided
            inventory_id = record.get('inventory_id') or f"INV{random.randint(100000, 999999)}"
            product_id = record.get('product_id') or f"PRD{random.randint(100000, 999999)}"
            id = record.get('id') or str(uuid.uuid4())

            # Create base inventory data with explicit empty strings for dates
            inventory_data = GoogleSyncInventoryCreate(
                id=id,
                product_id=product_id,
                inventory_id=inventory_id,
                sno=record.get('sno', f"SN{idx:04d}"),
                inventory_name=record['material'],
                material=record.get('material', ''),
                total_quantity=record.get('total_quantity', 0),
                manufacturer=record.get('manufacturer', 'Unknown'),
                purchase_dealer=record.get('purchase_dealer', 'Unknown'),
                purchase_date=record.get('purchase_date'),  # Let validator handle None
                purchase_amount=record.get('purchase_amount', 0),
                repair_quantity=record.get('repair_quantity', 0),
                repair_cost=record.get('repair_cost', 0),
                vendor_name=record.get('vendor_name', 'Unknown'),
                total_rent=record.get('total_rent', 0),
                rented_inventory_returned=record.get('rented_inventory_returned', False),
                returned_date=record.get('returned_date'),  # Let validator handle None
                issued_qty=record.get('issued_qty', 0),
                balance_qty=record.get('balance_qty', 0),
                submitted_by="System Sync",
                updated_at=UTCDateUtils.get_current_datetime(),
                created_at=UTCDateUtils.get_current_datetime()
            )
        
            # Process and validate boolean fields
            boolean_fields = {
                'on_rent': False,
                'rented_inventory_returned': False,
                'on_event': False,
                'in_office': False,
                'in_warehouse': False
            }
            for field, default_value in boolean_fields.items():
                val = getattr(inventory_data, field, default_value)
                setattr(inventory_data, field, BaseValidators.validate_boolean_fields(val))

            # Generate barcode if not provided
            if not inventory_data.inventory_barcode:
                barcode_data = {
                    'inventory_name': inventory_data.inventory_name,
                    'inventory_id': inventory_data.inventory_id,
                    'id': id
                }
                barcode, unique_code = self.barcode_generator.generate_linked_codes(barcode_data)
                inventory_data.inventory_barcode = barcode
                inventory_data.inventory_unique_code = unique_code
                inventory_data.inventory_barcode_url = ""

            return inventory_data

        except Exception as e:
            logger.error(f"Error processing row {idx}: {str(e)}", exc_info=True)
            return None

    async def sync_inventory_from_google_sheets(self, request: Request) -> List[InventoryRedisOut]:
        try:
            logger.info("Starting Google Sheets sync")
            records = await self._fetch_sheet_data()
            logger.info(f"Total records fetched from Google Sheets: {len(records)}")
            
            if not records:
                logger.warning("No records found in Google Sheets")
                return []

            synced_items = []
            for idx, record in enumerate(records, start=1):
                try:
                    logger.debug(f"Processing row {idx}: {record.get('material')}")
                    
                    # Skip if essential data is missing
                    if not record.get('material'):
                        logger.warning(f"Skipping row {idx} - missing material name")
                        continue

                    inventory_data = await self._process_sheet_row(record, idx)
                    if not inventory_data:
                        logger.warning(f"Skipping row {idx} - failed to process")
                        continue

                    # Convert to dict and force include date fields
                    inventory_dict = inventory_data.model_dump(exclude_unset=False)

                    redis_key = f"inventory:{inventory_data.inventory_name}{inventory_data.inventory_id}"
                    
                    await self.redis.set(
                        redis_key,
                        json.dumps(inventory_dict, default=str),
                        ex=200
                    )
                    
                    synced_items.append(InventoryRedisOut(**inventory_dict))
                    logger.debug(f"Successfully processed row {idx}")

                except Exception as e:
                    logger.error(f"Error processing row {idx}: {str(e)}", exc_info=True)
                    continue

            logger.info(f"Sync completed. Success: {len(synced_items)}/{len(records)}")
            return synced_items

        except Exception as e:
            logger.error(f"Critical sync error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Sync failed: {str(e)}"
            )
    
# import asyncio
# from backend.app.config import REDIS_URL
# if __name__ == "__main__":
#     from fastapi import Request
#     from starlette.requests import Request as StarletteRequest  # or mock one

#     async def main():
#         # Connect to Redis (ensure Redis is running)
#         redis = await aioredis.from_url(REDIS_URL)

#         # Create the sync instance
#         syncer = GoogleSheetsToRedisSyncService(redis)

#         # Create a fake Request object if needed (depends on FastAPI setup)
#         request = StarletteRequest(scope={"type": "http"})

#         # Run sync
#         result = await syncer.sync_inventory_from_google_sheets(request)
#         print(f"Synced {len(result)} items.")

#     asyncio.run(main())

