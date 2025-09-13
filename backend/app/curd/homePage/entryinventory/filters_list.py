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

    async def show_all_inventory_paginated(self, db: AsyncSession, page: int = 1, per_page: int = 20):
        """Get paginated inventory - Redis first, database fallback with deduplication"""
        try:
            from app.pagination import paginate_data
            import pandas as pd
            
            # Get data from database first
            db_records = []
            try:
                from app.curd.entry_inverntory_curd import EntryInventoryService
                db_service = EntryInventoryService(self.redis)
                
                # Get from database using proper service
                result = await db_service.get_all_entries(db)
                if result:
                    stmt = select(EntryInventory)
                    db_result = await db.execute(stmt)
                    db_items = db_result.scalars().all()
                    db_records = [item.__dict__ for item in db_items]
                    logger.info(f"Found {len(db_records)} records in database")
            except Exception as e:
                logger.warning(f"Database fetch failed: {e}")
                db_records = []
            
            # Get data from Redis as fallback
            redis_records = []
            if not db_records:  # Only use Redis if database is empty
                try:
                    keys = await self.redis.keys("inventory:*")
                    for key in keys:
                        data = await self.redis.get(key)
                        if data:
                            try:
                                inventory_data = json.loads(data)
                                # Remove fields not in schema
                                inventory_data.pop('inventory_type', None)
                                redis_records.append(inventory_data)
                            except Exception as e:
                                logger.warning(f"Failed to parse Redis data for key {key}: {e}")
                                continue
                    logger.info(f"Using {len(redis_records)} Redis records as fallback")
                except Exception as e:
                    logger.warning(f"Redis fallback failed: {e}")
                    redis_records = []
            
            # Use database data primarily, Redis only as complete fallback
            all_records = db_records if db_records else redis_records
            
            if not all_records:
                raise HTTPException(status_code=404, detail="No inventory data available")
            
            # Sort alphabetically
            df_sorted = pd.DataFrame(all_records)
            df_sorted = df_sorted.sort_values('inventory_name', key=lambda x: x.str.lower())
            sorted_records = df_sorted.to_dict('records')
            
            # Apply pagination
            paginated_result = paginate_data(sorted_records, page=page, per_page=per_page)
            
            # Convert to schema format
            from app.schema.entry_inventory_schema import PaginatedInventoryResponse
            inventory_items = []
            for item in paginated_result['data']:
                try:
                    # Handle NaN values and clean data
                    cleaned_item = {}
                    for key, value in item.items():
                        if pd.isna(value) or value == 'nan':
                            cleaned_item[key] = None
                        else:
                            cleaned_item[key] = value
                    
                    inventory_items.append(InventoryRedisOut(**cleaned_item))
                except Exception as e:
                    logger.warning(f"Skipping invalid item: {e}")
                    continue
            
            return PaginatedInventoryResponse(
                data=inventory_items,
                pagination=paginated_result['pagination']
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Pagination failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve inventory data: {str(e)}")

