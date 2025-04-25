import os
import json
import gspread
import redis
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from backend.app.config import REDIS_URL

# Load environment variables
load_dotenv()

# Load Google service account credentials
SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT",
    os.path.join(os.path.dirname(__file__), "..", "credentials", "office-inventory-457815-1b466ac001f7.json")
)

# Define scopes and create credentials
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

# Authorize and access Google Sheet
gc = gspread.authorize(creds)
sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Zfz3R89APsXWb87P4aF5iH0jaFoxr7Lll8_raRkaJD8").sheet1

# Expected headers in the sheet
expected_headers = [
    "sno", "material", "total_quantity", "manufacturer", 
    "repair_quantity", "repair_cost", "issued_qty", "balance_qty"
]

# Get the records from the sheet
records = sheet.get_all_records(expected_headers=expected_headers)
print("Fetched records:", records)

# Connect to Redis using configuration
redis_client = redis.Redis.from_url(REDIS_URL)

# Store the records in Redis
redis_key = "inventory_data"
redis_client.set(redis_key, json.dumps(records))
print(f"Stored {len(records)} records in Redis under key: '{redis_key}'")









# import os
# import gspread
# from redis import asyncio as aioredis
# from fastapi import HTTPException
# from google.oauth2.service_account import Credentials
# import httpx
# import json
# import csv
# from io import StringIO
# import uuid
# import logging
# import random
# from datetime import datetime
# from dotenv import load_dotenv

# logger = logging.getLogger(__name__)

# class GoogleSheetsToRedisSync:
#     def __init__(self, redis_client: aioredis.Redis):
#         self.redis = redis_client
#         self.spreadsheet_key = "1Zfz3R89APsXWb87P4aF5iH0jaFoxr7Lll8_raRkaJD8"
#         self.sheet_name = "testing"
        
#         # Load environment variables
#         load_dotenv()
        
#         # Define expected headers (must match and be unique)
#         self.expected_headers = [
#             "sno", "material", "total_quantity", "manufacturer", 
#             "repair_quantity", "repair_cost", "issued_qty", "balance_qty"
#         ]
        
#         # Get service account file path from environment or use default
#         self.service_account_path = os.getenv(
#             "GOOGLE_SERVICE_ACCOUNT",
#             os.path.join(os.path.dirname(__file__), "..", "credentials", "office-inventory-457815-1b466ac001f7.json")
#         )

#     async def _get_google_sheets_client(self):
#         try:
#             creds = Credentials.from_service_account_file(
#                 self.service_account_path, 
#                 scopes=[
#                     "https://www.googleapis.com/auth/spreadsheets",
#                     "https://www.googleapis.com/auth/drive"
#                 ]
#             )
#             logger.info("Successfully created Google Sheets credentials")
#             return gspread.authorize(creds)
#         except Exception as e:
#             logger.error(f"Authentication failed: {str(e)}")
#             raise HTTPException(status_code=500, detail="Google Sheets auth failed")

#     async def _fetch_sheet_data(self):
#         try:
#             # Try via API with expected headers
#             try:
#                 gc = await self._get_google_sheets_client()
#                 spreadsheet = gc.open_by_key(self.spreadsheet_key)
#                 sheet = spreadsheet.sheet1  # Using sheet1 instead of worksheet name
                
#                 # Use get_all_records with expected headers
#                 records = sheet.get_all_records(expected_headers=self.expected_headers)
#                 logger.info(f"Fetched {len(records)} records via API with expected headers")
#                 return records
#             except Exception as api_error:
#                 logger.warning(f"API with headers failed, trying without headers: {api_error}")
                
#                 # Fallback without expected headers
#                 try:
#                     records = sheet.get_all_records()
#                     logger.info(f"Fetched {len(records)} records via API without headers")
#                     return records
#                 except Exception as api_error_2:
#                     logger.warning(f"API completely failed, using CSV fallback: {api_error_2}")

#                     # Final fallback via CSV
#                     csv_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_key}/export?format=csv"
#                     async with httpx.AsyncClient() as client:
#                         response = await client.get(csv_url)
#                         response.raise_for_status()
#                         reader = csv.DictReader(StringIO(response.text))
#                         records = [row for row in reader]
#                         logger.info(f"Fetched {len(records)} records via CSV fallback")
#                         return records

#         except Exception as e:
#             logger.error(f"Fetching sheet data failed: {str(e)}")
#             raise HTTPException(status_code=500, detail="Failed to fetch Google Sheet")

#     async def sync_to_redis(self):
#         try:
#             records = await self._fetch_sheet_data()
#             logger.info(f"Processing {len(records)} records for Redis sync")
            
#             if not records:
#                 logger.info("No records found.")
#                 return []

#             synced = 0
#             for idx, row in enumerate(records):
#                 try:
#                     inventory_id = f"INV{random.randint(100000, 999999)}"
#                     inventory_name = row.get('Material') or row.get('material') or f"Item{idx}"
#                     id = str(uuid.uuid4())

#                     data = {
#                         "id": id,
#                         "sno": row.get("sno", idx + 1),  # Using idx+1 to match spreadsheet row numbers
#                         "inventory_id": inventory_id,
#                         "inventory_name": inventory_name,
#                         "material": inventory_name,
#                         "total_quantity": int(row.get("total_quantity", 0)),
#                         "manufacturer": row.get("manufacturer", ""),
#                         "repair_quantity": int(row.get("repair_quantity", 0)),
#                         "repair_cost": float(row.get("repair_cost", 0)),
#                         "issued_qty": int(row.get("issued_qty", 0)),
#                         "balance_qty": int(row.get("balance_qty", 0)),
#                         "submitted_by": "System Sync",
#                         "created_at": datetime.utcnow().isoformat(),
#                         "updated_at": datetime.utcnow().isoformat()
#                     }

#                     redis_key = f"inventory:{inventory_name}:{inventory_id}"
#                     await self.redis.set(redis_key, json.dumps(data, default=str))
#                     synced += 1
#                 except Exception as e:
#                     logger.error(f"Error syncing row {idx + 1}: {str(e)}", exc_info=True)

#             logger.info(f"Successfully synced {synced}/{len(records)} records.")
#             return synced

#         except Exception as e:
#             logger.critical(f"Sync failed: {str(e)}", exc_info=True)
#             raise HTTPException(status_code=500, detail="Redis sync failed")
