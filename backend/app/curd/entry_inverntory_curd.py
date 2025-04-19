# backend/app/routers/entry_inventory_curd.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, time, timedelta, timezone
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.schema.entry_inventory_schema import (
    EntryInventoryCreate, 
    EntryInventoryUpdate,
    EntryInventoryOut,
    EntryInventorySearch,
    InventoryRedisOut,
    StoreInventoryRedis,
    DateRangeFilter
)
# Google Sheets API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account


from sqlalchemy.exc import SQLAlchemyError
from backend.app.interface.entry_inverntory_interface import EntryInventoryInterface
import logging
import uuid
from fastapi import HTTPException
from typing import List, Optional
from backend.app.database.redisclient import redis_client
from backend.app import config
from backend.app.utils.barcode_generator import BarcodeGenerator
from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
import random

from typing import Union
import json
import redis.asyncio as redis
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------
# CRUD OPERATIONS
# ------------------------ 

# Google API Scopes
SCOPES = os.getenv('GOOGLE_API_SCOPES').split(',')

from backend.app.utils.date_utils import UTCDateUtils
from backend.app.utils.field_validators import BaseValidators
class EntryInventoryService(EntryInventoryInterface):
    """Implementation of EntryInventoryInterface with async operations"""
    def __init__(self, base_url: str = config.BASE_URL, redis_client: redis.Redis = redis_client):
        self.base_url = base_url
        self.redis = redis_client
        self.barcode_generator = BarcodeGenerator()
        self.spreadsheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.admin_email = os.getenv('ADMIN_EMAIL')

# Create new entry of inventory for to_event which is directly stored in redis
    async def create_entry_inventory(self, db: AsyncSession, entry_data: EntryInventoryCreate) -> EntryInventory:
        """
        Create a new inventory entry stored permanently in Redis (no database storage).
        """
        try:
            # Convert input data to dictionary
            if isinstance(entry_data, EntryInventoryCreate):
                inventory_data = entry_data.model_dump(exclude_unset=True)
            else:
                inventory_data = entry_data

            # Generate ID if not provided
            if not inventory_data.get('id'):
                inventory_id = str(uuid.uuid4())
                inventory_data['id'] = inventory_id

            # Set timestamps (server-side only)
            current_time = UTCDateUtils.get_current_datetime()
            inventory_data['updated_at'] = current_time
            inventory_data['created_at'] = current_time 

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
            if not inventory_data.get('inventory_barcode'):
                barcode_data = {
                    'inventory_name': inventory_data['inventory_name'],
                    'inventory_id': inventory_data['inventory_id'],
                    'id': inventory_id 
                }
                barcode, unique_code = self.barcode_generator.generate_linked_codes(barcode_data)
                inventory_data.update({
                    'inventory_barcode': barcode,
                    'inventory_unique_code': unique_code,
                    'inventory_barcode_url': inventory_data.get('inventory_barcode_url', "")
                })

            # Permanent Redis storage (no expiration)
            redis_key = f"inventory:{inventory_data['inventory_name']}{inventory_data['inventory_id']}"
            await self.redis.set(
                redis_key,
                json.dumps(inventory_data, default=str)
            )
            return EntryInventory(**inventory_data)

        except KeyError as ke:
            logger.error(f"Missing required field: {str(ke)}")
            raise HTTPException(status_code=400, detail=f"Missing required field: {str(ke)}")
        except (TypeError, ValueError) as e:  # Changed from JSONEncodeError
            logger.error(f"JSON encoding error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid inventory data format")
        except Exception as e:
            logger.error(f"Redis storage failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create inventory assignment: {str(e)}"
            )

#  Filter inventory by date range without any `IDs`
    async def get_by_date_range(
        self,
        db: AsyncSession,
        date_range_filter: DateRangeFilter,
        skip: int = 0
    ) -> List[EntryInventory]:
        try:
            # Handle both string and date inputs
            start_date = (
                UTCDateUtils.parse_date(date_range_filter.from_date)
                if isinstance(date_range_filter.from_date, str)
                else date_range_filter.from_date
            )
            end_date = (
                UTCDateUtils.parse_date(date_range_filter.to_date)
                if isinstance(date_range_filter.to_date, str)
                else date_range_filter.to_date
            )
            
            if not start_date or not end_date:
                raise ValueError("Invalid date range provided")
            
            # Get all inventory keys
            keys = await self.redis.keys("inventory:*")
            filtered_items = []
            
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        item_data = json.loads(data)
                        created_at_str = item_data.get('created_at')
                        if not created_at_str:
                            continue
                            
                        created_at = UTCDateUtils.parse_datetime(created_at_str)
                        if not created_at:
                            continue
                            
                        # Check if within date range
                        if start_date <= created_at.date() <= end_date:
                            # Convert timestamps using UTCDateUtils
                            item_data['created_at'] = UTCDateUtils.validate_datetime_field(item_data.get('created_at'))
                            item_data['updated_at'] = UTCDateUtils.validate_datetime_field(item_data.get('updated_at'))
                            filtered_items.append(EntryInventoryOut(**item_data))
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Skipping invalid inventory item {key}: {str(e)}")
                        continue
            
            # Sort by created_at (newest first)
            filtered_items.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            return filtered_items[skip : skip + 1000]

        except Exception as e:
            logger.error(f"Date range filter failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching inventory by date range: {str(e)}"
            )

    # READ ALL: Get all inventory entries directly from redis
    async def get_all_entries(self, db: AsyncSession, skip: int = 0) -> List[InventoryRedisOut]:
        try:
            # Get all keys matching your project pattern
            keys = await self.redis.keys("inventory:*")
            
            projects = []
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        assigned_data = json.loads(data)
                        # Handle the 'cretaed_at' typo if present
                        if 'cretaed_at' in assigned_data and assigned_data['cretaed_at'] is not None:
                            assigned_data['created_at'] = assigned_data['cretaed_at']
                        # Validate the data against your schema
                        validated_project = InventoryRedisOut.model_validate(assigned_data)
                        projects.append(validated_project)
                    except ValidationError as ve:
                        logger.warning(f"Validation error for project {key}: {ve}")
                        continue
            
            # Sort by updated_at (descending)
            projects.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination
            paginated_projects = projects[skip:skip+1000]  # Assuming page size of 100
            
            return paginated_projects
        except Exception as e:
            logger.error(f"Redis error fetching entries: {e}")

    # READ: Get an inventory entry by its inventry_id
    async def get_by_inventory_id(self, db: AsyncSession, inventory_id: str) -> Optional[EntryInventoryOut]:
        try:
            # Search all inventory keys in Redis
            keys = await self.redis.keys("inventory:*")
            
            for key in keys:
                # Get the inventory data from Redis
                inventory_data = await self.redis.get(key)
                if inventory_data:
                    data = json.loads(inventory_data)
                    # Check if this is the inventory we're looking for
                    if data.get('inventory_id') == inventory_id:
                        # Convert string timestamps back to datetime objects
                        if 'updated_at' in data:
                            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                        return EntryInventoryOut(**data)
            
            return None  # Return None if not found

        except json.JSONDecodeError as je:
            logger.error(f"Error decoding Redis data: {str(je)}")
            raise HTTPException(
                status_code=500,
                detail="Error decoding inventory data"
            )
        except Exception as e:
            logger.error(f"Redis error fetching inventory: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error fetching inventory from Redis"
            )

# UPDATE: Update an existing inventory entry {} {Inventory ID}
    async def update_entry(self, db: AsyncSession, inventory_id: str, update_data: EntryInventoryUpdate):
        try:
            # Format inventory_id if needed
            if not inventory_id.startswith('INV'):
                inventory_id = f"INV{inventory_id}"

            # Search all inventory keys to find matching inventory_id
            keys = await self.redis.keys("inventory:*")
            redis_key = None
            
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    item_data = json.loads(data)
                    if item_data.get('inventory_id') == inventory_id:
                        redis_key = key
                        break

            if not redis_key:
                raise HTTPException(
                    status_code=404,
                    detail=f"Inventory not found with ID: {inventory_id}"
                )

            # Get existing record from Redis
            existing_data = await self.redis.get(redis_key)
            if not existing_data:
                raise HTTPException(
                    status_code=404,
                    detail="Inventory data not found in Redis"
                )

            existing_dict = json.loads(existing_data)
            
            # Convert update_data to dict and exclude unset fields
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Define immutable fields that shouldn't be updated
            IMMUTABLE_FIELDS = {
                'id', 'sno', 'inventory_id', 'product_id', 
                'created_at', 'inventory_barcode', 
                'inventory_unique_code', 'inventory_barcode_url'
            }

            # Apply updates while preserving immutable fields
            updated_dict = existing_dict.copy()
            for field, value in update_dict.items():
                if field not in IMMUTABLE_FIELDS:
                    updated_dict[field] = value

            # Always update the timestamp with UTC timezone
            updated_dict['updated_at'] = UTCDateUtils.get_current_datetime().isoformat()

            # Save back to Redis
            await self.redis.set(
                redis_key,
                json.dumps(updated_dict, default=str)
            )

            return EntryInventoryOut(**updated_dict)

        except HTTPException:
            raise
        except json.JSONDecodeError as je:
            logger.error(f"JSON decode error: {str(je)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid inventory data format in Redis"
            )
        except Exception as e:
            logger.error(f"Redis update failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update inventory: {str(e)}"
            )
    
    # DELETE: Delete an inventory entry by  {Inventory ID}
    async def delete_entry(self, db: AsyncSession, inventory_id: str) -> bool:
        try:
            # Format inventory_id if needed
            if not inventory_id.startswith('INV'):
                inventory_id = f"INV{inventory_id}"

            # Search all inventory keys to find matching inventory_id
            keys = await self.redis.keys("inventory:*")
            redis_key = None
            
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    item_data = json.loads(data)
                    if item_data.get('inventory_id') == inventory_id:
                        redis_key = key
                        break

            if not redis_key:
                return False

            # Delete the key from Redis
            await self.redis.delete(redis_key)
            
            # Also delete from secondary index if you have one
            await self.redis.delete(f"inventory_index:{inventory_id}")
            
            return True

        except Exception as e:
            logger.error(f"Redis delete failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete inventory: {str(e)}"
            )
            
# Search inventory items by various criteria {Product ID, Inventory ID} from redis
    async def search_entries(
        self, 
        db: AsyncSession,
        inventory_id: Optional[str] = None,
        product_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[EntryInventoryOut]:
        """
        Search inventory entries by exactly one of:
        - inventory_id
        - product_id
        - project_id
        """
        try:
            # Get all inventory keys from Redis
            keys = await self.redis.keys("inventory:*")
            matching_items = []
            
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        item_data = json.loads(data)
                        
                        # Check search criteria
                        match = False
                        if inventory_id and item_data.get('inventory_id') == inventory_id:
                            match = True
                        elif product_id and item_data.get('product_id') == product_id:
                            match = True
                        elif project_id and item_data.get('project_id') == project_id:
                            match = True
                        
                        if match:
                            # Clean the item data before creating the model
                            clean_item_data = {
                                k: v for k, v in item_data.items()
                                if k in EntryInventoryOut.model_fields
                            }
                            matching_items.append(EntryInventoryOut(**clean_item_data))
                            
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.warning(f"Skipping invalid inventory data in key {key}: {str(e)}")
                        continue
            
            return matching_items

        except Exception as e:
            logger.error(f"Redis search failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error searching inventory items: {str(e)}"
            )

# ------------------------------------------------------------------------------------------------------------------------------------------------
#  inventory entries directly from local databases  (no search) according in sequence alphabetical order after clicking `Show All` button
# ------------------------------------------------------------------------------------------------------------------------------------------------

    #  Show all inventory entries directly from local Redis after clicking {Show All} button
    async def show_all_inventory_from_redis(self) -> List[InventoryRedisOut]:
        """Retrieve all inventory entries from Redis"""
        try:
            # Get all inventory keys from Redis
            keys = await redis_client.keys("inventory:*")

            # Retrieve and parse all entries
            entries = []
            for key in keys:
                data = await redis_client.get(key)
                if data:
                    entries.append(InventoryRedisOut.from_redis(data))

            # Sort by name (alphabetical)
            entries.sort(key=lambda x: x.name)
            return entries

        except Exception as e:
            logger.error(f"Redis retrieval error: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to load from Redis"
            )

    # List all inventory entries function
    async def list_entry_inventories_curd(self, db: AsyncSession):
        try:
            # Get all inventory keys from Redis
            keys = await self.redis.keys("inventory:*")
            all_entries = []
            
            for key in keys:
                inventory_data = await self.redis.get(key)
                if inventory_data:
                    try:
                        data = json.loads(inventory_data)
                        # Convert timestamps if they exist
                        if 'created_at' in data:
                            data['created_at'] = datetime.fromisoformat(data['created_at'])
                        if 'updated_at' in data:
                            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                        # Validate against schema
                        entry = EntryInventoryOut(**data)
                        all_entries.append(entry)
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.warning(f"Skipping invalid inventory data in key {key}: {str(e)}")
                        continue
            
            # Sort by created_at (newest first)
            all_entries.sort(key=lambda x: x.created_at, reverse=True)
            
            return all_entries

        except Exception as e:
            logger.error(f"Redis list failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error listing inventory items"
            )

    #  Store all recored in Redis after clicking {sync} button
    async def sync_inventory_from_google_sheets(self) -> List[InventoryRedisOut]:
        """
        Sync inventory data from Google Sheets to Redis using direct email access
        
        Returns:
            List[InventoryRedisOut]: List of synced inventory items
        """
        try:
            # Directly authenticate with gspread using the email
            gc = gspread.oauth(
                credentials_filename='credentials.json',
                authorized_user_filename='authorized_user.json'
            )
            
            # Open the spreadsheet
            sheet = gc.open_by_key(self.spreadsheet_id).sheet1
            records = sheet.get_all_records()
            
            synced_items = []
            
            for idx, record in enumerate(records, start=1):
                try:
                    # Generate IDs if not present
                    inventory_id = f"INV{random.randint(100000, 999999)}"
                    product_id = f"PRD{random.randint(100000, 999999)}"
                    
                    # Create inventory data dictionary
                    inventory_data = {
                        'id': str(uuid.uuid4()),
                        'sno': f"SN{idx:04d}",
                        'inventory_id': inventory_id,
                        'product_id': product_id,
                        'inventory_name': record['Material'],
                        'material': record.get('Material', ''),
                        'total_quantity': str(record['Total Quantity']),
                        'manufacturer': record.get('Manufacturer', ''),
                        'purchase_dealer': '',
                        'purchase_date': '',
                        'purchase_amount': '',
                        'repair_quantity': str(record.get('Repair Quantity', 0)),
                        'repair_cost': str(record.get('Repair Cost', 0)),
                        'on_rent': "false",
                        'vendor_name': '',
                        'total_rent': '',
                        'rented_inventory_returned': "false",
                        'on_event': "false",
                        'in_office': "true",
                        'in_warehouse': "false",
                        'issued_qty': str(record.get('Issued Qty', 0)),
                        'balance_qty': str(record.get('Balance Qty', 0)),
                        'submitted_by': "System Sync",
                        'inventory_barcode': '',
                        'inventory_barcode_url': '',
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }

                    # Generate barcode
                    barcode, unique_code = self.barcode_generator.generate_linked_codes({
                        'inventory_name': inventory_data['inventory_name'],
                        'inventory_id': inventory_data['inventory_id'],
                        'id': inventory_data['id']
                    })
                    inventory_data.update({
                        'inventory_barcode': barcode,
                        'inventory_unique_code': unique_code
                    })

                    # Store in Redis
                    redis_key = f"inventory:{inventory_data['inventory_name']}{inventory_data['inventory_id']}"
                    await self.redis.set(
                        redis_key,
                        json.dumps(inventory_data, default=str)
                    )
                    
                    synced_items.append(InventoryRedisOut(**inventory_data))
                    
                except Exception as e:
                    logger.warning(f"Error processing row {idx}: {str(e)}")
                    continue
            
            return synced_items
            
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to sync inventory from Google Sheets"
            )