# ~/app/curd/homePage/entryinventory/filters_list.py

from app.utils.common_imports import *

from app.models.entry_inventory_model import EntryInventory
from app.schema.entry_inventory_schema import (
    EntryInventoryCreate, 
    EntryInventoryUpdate,
    EntryInventoryOut,
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
from app.interface.entry_inverntory_interface import EntryInventoryInterface

# ------------------------
# SHOW ALL LIST ACCORDING TO PAGINATIONS  OPERATIONS
# ------------------------ 

class FiltersListPaginationService(EntryInventoryInterface):
    """Implementation of EntryInventoryInterface with async operations"""
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.qr_generator = QRCodeGenerator()
        self.InventoryUpdater = InventoryUpdater(redis_client)
        self.barcode_generator = DynamicBarcodeGenerator()
        self.base_url = config.BASE_URL
    
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


## List all inventory entries function
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


#  Show all inventory entries directly from local Redis after clicking {Show All} button
    async def show_all_inventory_from_redis(self) -> List[InventoryRedisOut]:
        """Retrieve all inventory entries from Redis"""
        try:
            # Get all inventory keys from Redis
            keys = await self.redis.keys("inventory:*")

            # Retrieve and parse all entries
            entries = []
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        entry_data = json.loads(data)
                        entries.append(InventoryRedisOut(**entry_data))
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.warning(f"Skipping invalid inventory data in key {key}: {str(e)}")
                        continue

            # Sort by inventory_name (alphabetical)
            entries.sort(key=lambda x: x.inventory_name.lower())
            return entries

        except Exception as e:
            logger.error(f"Redis retrieval error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Failed to load inventory from Redis"
            )

