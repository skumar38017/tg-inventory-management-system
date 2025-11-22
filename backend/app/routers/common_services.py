from app.utils.common_imports import *

from app.curd.homePage.entryinventory.create_inventory import CreateInventoryService
from app.curd.homePage.entryinventory.filters_list import FiltersListPaginationService
from app.curd.google_sheet_redis_inventory import GoogleSheetsToRedisSyncService
from app.curd.entry_inverntory_curd import EntryInventoryService


# Dependency to get the entry inventory service
def get_create_inventory_service(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> CreateInventoryService:
    return CreateInventoryService(redis)

# Dependency to get the entry inventory service
def get_filters_list_service(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> FiltersListPaginationService:
    return FiltersListPaginationService(redis)

# Dependency to get the entry inventory service
def get_entryget_inventory_from_google_sheet(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> GoogleSheetsToRedisSyncService:
    return GoogleSheetsToRedisSyncService(redis)

# Dependency to get the entry inventory service
def get_entry_inventory_service(
    redis: aioredis.Redis = Depends(get_redis_dependency)
) -> EntryInventoryService:
    return EntryInventoryService(redis)