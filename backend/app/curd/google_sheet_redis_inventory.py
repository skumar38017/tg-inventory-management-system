# backend/app/curd/google_sheet_curd.py
from backend.app.utils.common_imports import *

import gspread
from google.oauth2.service_account import Credentials
from starlette.requests import Request as StarletteRequest
from backend.app.schema.entry_inventory_schema import (
    GoogleSyncInventoryCreate,
    InventoryRedisOut
)
from backend.app.interface.entry_inverntory_interface import GoogleSyncInventoryInterface
from google.oauth2 import service_account
from dotenv import load_dotenv

class GoogleSheetsToRedisSyncService(GoogleSyncInventoryInterface):
    """Implementation of GoogleSyncInventoryInterface with async operations"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.barcode_generator = DynamicBarcodeGenerator()
        self.qr_generator = QRCodeGenerator()
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
        """Fetch data from Google Sheets, only getting expected columns"""
        try:
            gc = await self._get_google_sheets_client()
            spreadsheet = gc.open_by_url(self.spreadsheet_url)
            worksheet = spreadsheet.worksheet(self.sheet_name)
            
            # Get all values first
            all_values = worksheet.get_all_values()
            
            if not all_values:
                raise HTTPException(
                    status_code=400,
                    detail="Empty worksheet - no data found"
                )
            
            # Get actual headers from first row
            actual_headers = [h.strip().lower() for h in all_values[0]]
            
            # Find which expected headers exist in the sheet
            valid_headers = []
            for expected in self.expected_headers:
                if expected in actual_headers:
                    valid_headers.append(expected)
                else:
                    logger.warning(f"Expected column '{expected}' not found in sheet")
            
            if not valid_headers:
                raise HTTPException(
                    status_code=400,
                    detail="No matching columns found between sheet and expected headers"
                )
            
            # Get only the valid columns we care about
            records = worksheet.get_all_records(
                expected_headers=valid_headers,
                head=1  # Skip header row
            )
            
            logger.info(f"Fetched {len(records)} records from Google Sheets")
            return records
            
        except HTTPException:
            raise
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

    async def _process_sheet_row(self, record: dict, idx: int, inventory_type: str) -> Optional[GoogleSyncInventoryCreate]:
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
                try:
                    # Generate minimal barcode with only bars, code, and unique code
                    barcode_value, unique_code, barcode_img = self.barcode_generator.generate_dynamic_barcode({
                        'inventory_id': inventory_data.inventory_id,
                        'inventory_name': inventory_data.inventory_name,
                        'type': inventory_type
                    })
                    
                    # Save barcode image
                    barcode_url = self.barcode_generator.save_barcode_image(
                        barcode_img,
                        inventory_data.inventory_id,
                        inventory_data.inventory_name,
                    )

                    # Update inventory data with barcode information
                    inventory_data.inventory_barcode = barcode_value
                    inventory_data.inventory_unique_code = unique_code
                    inventory_data.inventory_barcode_url = barcode_url

                except ValueError as e:
                    logger.error(f"Barcode generation failed: {str(e)}")
                    raise HTTPException(status_code=400, detail=str(e))

                # Generate QR code content first
                qr_content = self.qr_generator.generate_qr_content(inventory_data)

                # Then generate QR code with the content
                qr_bytes, filename, qr_url = self.qr_generator.generate_qr_code(
                    data=qr_content,
                    inventory_id=inventory_data.inventory_id,
                    inventory_name=inventory_data.inventory_name
                )

                # Add QR code URL to inventory data
                inventory_data.inventory_qrcode_url = qr_url

            return inventory_data

        except Exception as e:
            logger.error(f"Error processing row {idx}: {str(e)}", exc_info=True)
            return None

    async def sync_inventory_from_google_sheets(self, request: Request, inventory_type: str,) -> List[InventoryRedisOut]:
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

                    inventory_data = await self._process_sheet_row(record, idx, inventory_type=inventory_type)
                    if not inventory_data:
                        logger.warning(f"Skipping row {idx} - failed to process")
                        continue

                    # Convert to dict and force include date fields
                    inventory_dict = inventory_data.model_dump(exclude_unset=False)

                    # Create a search pattern for existing inventory
                    search_pattern = f"inventory:*{inventory_data.inventory_name}*"
                    
                    # Scan Redis for existing inventory with this name
                    existing_keys = []
                    async for key in self.redis.scan_iter(match=search_pattern):
                        existing_keys.append(key)
                    
                    if existing_keys:
                        # If found, update existing record
                        if len(existing_keys) > 1:
                            logger.warning(f"Multiple entries found for {inventory_data.inventory_name}, updating first match")
                        
                        existing_key = existing_keys[0]
                        existing_data = await self.redis.get(existing_key)
                        
                        if existing_data:
                            existing_dict = json.loads(existing_data)
                            
                            # Update only the allowed fields
                            update_fields = [
                                "sno", "total_quantity", "manufacturer",
                                "repair_quantity", "repair_cost", "issued_qty", 
                                "balance_qty"
                            ]
                            
                            for field in update_fields:
                                if field in inventory_dict:
                                    existing_dict[field] = inventory_dict[field]
                            
                            # Update timestamps
                            existing_dict['updated_at'] = UTCDateUtils.get_current_datetime()
                            
                            # Save back to Redis
                            await self.redis.set(
                                existing_key,
                                json.dumps(existing_dict, default=str),
                            )
                            
                            synced_items.append(InventoryRedisOut(**existing_dict))
                            logger.debug(f"Updated existing inventory: {inventory_data.inventory_name}")
                        else:
                            # If existing key but no data, treat as new
                            await self._create_new_inventory(inventory_dict)
                            synced_items.append(InventoryRedisOut(**inventory_dict))
                    else:
                        # If not found, create new record
                        await self._create_new_inventory(inventory_dict)
                        synced_items.append(InventoryRedisOut(**inventory_dict))

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

    async def _create_new_inventory(self, inventory_dict: dict):
        """Helper method to create new inventory in Redis"""
        # redis_key = f"inventory:{inventory_dict['inventory_name']}{inventory_dict['inventory_id']}"
        redis_key = f"inventory:{inventory_dict['inventory_name']}{inventory_dict['inventory_id']}"
        await self.redis.set(
            redis_key,
            json.dumps(inventory_dict, default=str)
        )
        logger.debug(f"Created new inventory: {inventory_dict['inventory_name']}")

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

