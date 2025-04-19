import gspread
from google.oauth2.service_account import Credentials
from fastapi import HTTPException, Request
from typing import List, Optional
import json
import random
import logging
import uuid
from datetime import datetime
from pydantic import BaseModel
from backend.app.utils.date_utils import UTCDateUtils
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryBase,
    EntryInventoryCreate,
    InventoryRedisOut
)
import httpx 
import os
from backend.app.utils.field_validators import BaseValidators
from backend.app.interface.entry_inverntory_interface import EntryInventoryInterface

import redis.asyncio as redis
from backend.app.database.redisclient import redis_client
from backend.app import config
from backend.app.utils.barcode_generator import BarcodeGenerator
from google_auth_oauthlib.flow import InstalledAppFlow



logger = logging.getLogger(__name__)

class GoogleSheetsToRedisSync(EntryInventoryInterface):
    """Implementation of EntryInventoryInterface with async operations"""

    def __init__(self, base_url: str = config.BASE_URL, redis_client: redis.Redis = redis_client):
 
        self.base_url = base_url
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()
        self.token_file = 'token.json'  # Will store the OAuth token
        self.scope = ['https://www.googleapis.com/auth/spreadsheets.readonly','https://docs.google.com/spreadsheets/d/1GCtZ7pcFsqcIvbkhq9q-b3YmBZxEQ120UCIU_X5CuP8/edit?usp=sharing']
        
    async def _get_google_sheets_client(self):
        """Simplified authentication with automatic token handling"""
        try:
            # Pre-configured credentials (you'll set this up once)
            if not os.path.exists('credentials.json'):
                raise HTTPException(
                    status_code=500,
                    detail="Missing credentials.json - setup required"
                )
                
            # Try to use existing token
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.scope)
                return gspread.authorize(creds)
                
            # First-time setup (automatic browser login)
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                self.scope
            )
            creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
                
            return gspread.authorize(creds)
            
        except Exception as e:
            logger.error(f"Auth failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Automatic authentication failed - check logs"
            )

    async def _process_sheet_row(self, record: dict, idx: int) -> Optional[EntryInventoryCreate]:
        """Process a single row from Google Sheets into EntryInventoryCreate"""
        try:
            if not record.get('Material'):
                return None

            # Generate IDs
            inventory_id = f"INV{random.randint(100000, 999999)}"
            product_id = f"PRD{random.randint(100000, 999999)}"
            id = str(uuid.uuid4())

            # Create base inventory data
            inventory_data = EntryInventoryCreate(
                id=id,
                product_id=product_id,
                inventory_id=inventory_id,
                sno=f"SN{idx:04d}",
                inventory_name=record['Material'],
                material=record.get('Material', ''),
                total_quantity=self._convert_quantity(record.get('Total Quantity', 0)),
                manufacturer=record.get('Manufacturer', ''),
                purchase_dealer=record.get('Purchase Dealer', ''),
                purchase_date=record.get('Purchase Date', ''),
                purchase_amount=self._convert_quantity(record.get('Purchase Amount', 0)),
                repair_quantity=self._convert_quantity(record.get('Repair Quantity', 0)),
                repair_cost=self._convert_quantity(record.get('Repair Cost', 0)),
                vendor_name=record.get('Vendor Name', ''),
                total_rent=self._convert_quantity(record.get('Total Rent', 0)),
                issued_qty=self._convert_quantity(record.get('Issued Qty', 0)),
                balance_qty=self._convert_quantity(record.get('Balance Qty', 0)),
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
                val = inventory_data.get(field, default_value)
                inventory_data[field] = BaseValidators.validate_boolean_fields(val)

            # Generate barcode if not provided
            if not inventory_data.inventory_barcode:
                barcode_data = {
                    'inventory_name': inventory_data.inventory_name,
                    'inventory_id': inventory_data.inventory_id,
                    'id': id
                }
            barcode, unique_code = self.barcode_generator.generate_linked_codes(barcode_data)
            inventory_data.update({
                'inventory_barcode': barcode,
                'inventory_unique_code': unique_code,
                'inventory_barcode_url': inventory_data.get('inventory_barcode_url', "")
            })

            return inventory_data

        except Exception as e:
            logger.error(f"Error processing row {idx}: {str(e)}")
            return None

    async def sync_inventory_from_google_sheets(self, request: Request) -> List[InventoryRedisOut]:
        """
        Sync inventory data from Google Sheets to Redis with enhanced error handling
        """
        try:
            # First try the API method with OAuth
            try:
                gc = await self._get_google_sheets_client()
                SPREADSHEET_KEY = "1GCtZ7pcFsqcIvbkhq9q-b3YmBZxEQ120UCIU_X5CuP8"
                WORKSHEET_INDEX = 0
                
                spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
                worksheet = spreadsheet.get_worksheet(WORKSHEET_INDEX)
                records = worksheet.get_all_records()
                
                logger.info(f"Successfully fetched {len(records)} records via Sheets API")
                
            except Exception as api_error:
                logger.warning(f"API access failed, trying CSV fallback: {str(api_error)}")
                
                # Fallback to CSV export if API fails
                CSV_URL = "https://docs.google.com/spreadsheets/d/1GCtZ7pcFsqcIvbkhq9q-b3YmBZxEQ120UCIU_X5CuP8/export?format=csv"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(CSV_URL)
                    response.raise_for_status()
                    csv_data = response.text

                # Parse CSV to list of dicts
                from io import StringIO
                import csv
                records = []
                reader = csv.DictReader(StringIO(csv_data))
                records = list(reader)
                logger.info(f"Successfully fetched {len(records)} records via CSV")

            # Process records
            synced_items = []
            success_count = 0
            error_count = 0
            
            for idx, record in enumerate(records, start=1):
                try:
                    # Debug: Log first record
                    if idx == 1:
                        logger.debug(f"First record sample: {dict(list(record.items())[:3])}")
                    
                    inventory_data = await self._process_sheet_row(record, idx)
                    if not inventory_data:
                        continue
                    
                    # Convert to dictionary for Redis storage
                    inventory_dict = inventory_data.model_dump(
                        exclude_unset=True,
                        exclude_none=True
                    )
                    
                    # Create unique Redis key
                    redis_key = f"inventory:{inventory_data.inventory_id}:{inventory_data.inventory_name}"
                    await self.redis.set(
                        redis_key,
                        json.dumps(inventory_dict, default=str),
                        ex=86400  # Optional: Set expiration (1 day)
                    )
                    
                    synced_items.append(InventoryRedisOut(**inventory_dict))
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Row {idx} failed: {str(e)}", exc_info=True)
                    continue
            
            logger.info(f"Sync completed: {success_count} items, {error_count} errors")
            return synced_items
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error accessing Google Sheets: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail="Failed to connect to Google Sheets"
            )
        except Exception as e:
            logger.error(f"Critical sync error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Sync failed: {str(e)}"
            )