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
import os
from backend.app.utils.field_validators import BaseValidators
from backend.app.interface.entry_inverntory_interface import GoogleSheetsToRedisSyncInterface

import redis.asyncio as redis
from backend.app.database.redisclient import redis_client
from backend.app import config
from backend.app.utils.barcode_generator import BarcodeGenerator
from google_auth_oauthlib.flow import InstalledAppFlow



logger = logging.getLogger(__name__)

class GoogleSheetsToRedisSync(GoogleSheetsToRedisSyncInterface):
    """Implementation of EntryInventoryInterface with async operations"""

    def __init__(self, base_url: str = config.BASE_URL, redis_client: redis.Redis = redis_client):
 
        self.base_url = base_url
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()
        self.token_file = 'token.json'  # Will store the OAuth token
        self.scope = ['https://www.googleapis.com/auth/spreadsheets.readonly','https://docs.google.com/spreadsheets/d/1GCtZ7pcFsqcIvbkhq9q-b3YmBZxEQ120UCIU_X5CuP8/edit?usp=sharing']
        
    async def _get_google_sheets_client(self):
        """Authenticate with Google Sheets API using OAuth"""
        try:
            creds = None
            
            # If token exists, use it
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.scope)
            
            # If no valid credentials, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json',  # You'll need to create this
                        self.scope
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            return gspread.authorize(creds)
            
        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to authenticate with Google Sheets"
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
        Securely sync inventory data from Google Sheets to Redis
        
        Args:
            request: FastAPI request object
            
        Returns:
            List of successfully synced inventory items
            
        Raises:
            HTTPException: If sync fails
        """
        try:
            gc = await self._get_google_sheets_client()
            SPREADSHEET_KEY = "1GCtZ7pcFsqcIvbkhq9q-b3YmBZxEQ120UCIU_X5CuP8"
            WORKSHEET_INDEX = 0
            
            try:
                spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
                worksheet = spreadsheet.get_worksheet(WORKSHEET_INDEX)
                records = worksheet.get_all_records()
            except Exception as e:
                logger.error(f"Failed to access Google Sheet: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Could not access Google Sheets data"
                )
            
            synced_items = []
            success_count = 0
            error_count = 0
            
            for idx, record in enumerate(records, start=1):
                try:
                    inventory_data = await self._process_sheet_row(record, idx)
                    if not inventory_data:
                        continue
                    
                    # Convert to dictionary for Redis storage
                    inventory_dict = inventory_data.model_dump(
                        exclude_unset=True,
                        exclude_none=True
                    )
                    
                    # Store in Redis
                    redis_key = f"inventory:{inventory_data.inventory_id}"
                    await self.redis.set(
                        redis_key,
                        json.dumps(inventory_dict, default=str)
                    )
                    
                    # Convert to output schema
                    synced_items.append(InventoryRedisOut(**inventory_dict))
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Failed to process row {idx}: {str(e)}")
                    continue
            
            logger.info(
                f"Sync completed: {success_count} successful, {error_count} errors"
            )
            
            return synced_items
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to sync inventory: {str(e)}"
            )