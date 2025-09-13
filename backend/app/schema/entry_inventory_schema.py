# backend/app/schema/entry_inventory_schema.py
import json
from typing import Optional, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict
from app.utils.field_validators import BaseValidators
from app.utils.date_utils import UTCDateUtils

class EntryInventoryBase(BaseValidators, BaseModel):
    product_id: Optional[str] = None  
    inventory_id: Optional[str] = None  
    sno: Optional[str] = None
    inventory_name: Optional[str] = Field(None, alias='name')
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[Union[str, date]] = None
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: Optional[str] = "false" 
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[str] = "false" 
    returned_date: Optional[Union[str, date]] = None 
    on_event: Optional[str] = "false"  
    in_office: Optional[str] = "false"  
    in_warehouse: Optional[str] = "false"  
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )
# Schema for creating or updating EntryInventory (without id and timestamps)
class EntryInventoryCreate(EntryInventoryBase):
    pass

class EntryInventoryOut(EntryInventoryBase):
    id: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    inventory_barcode: Optional[Union[str, int]] = None
    inventory_unique_code: Optional[Union[str, int]] = None
    inventory_barcode_url: Optional[str] = None
    inventory_qrcode_url: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )
    
class EntryInventoryUpdate(BaseValidators, BaseModel):
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[Union[str, date]] = None 
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: Optional[bool] = None
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[bool] = None
    returned_date: Optional[Union[str, date]] = None 
    on_event: Optional[bool] = None
    in_office: Optional[bool] = None
    in_warehouse: Optional[bool] = None
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )


class EntryInventoryUpdateOut(EntryInventoryOut):
    pass
        
# Schema for Search EntryInventory (includes invetory_id and timestamp fields)
class EntryInventorySearch(BaseValidators, BaseModel):
    inventory_id: Optional[str] = None
    product_id: Optional[str] = None
    project_id: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v),
        }
    )

# Schema for search date range filter
class DateRangeFilter(BaseValidators, BaseModel):
    from_date: Union[str, date]
    to_date: Union[str, date]

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )

class DateRangeFilterOut(EntryInventoryOut):
    pass

class SyncInventoryOut(EntryInventoryOut):
    pass

# Schema for Store record in Redis after clicking {sync} button
class StoreInventoryRedis(BaseValidators, BaseModel):
    id: Optional[Union[str, int]] = None
    sno: Optional[Union[str, int]] = None
    inventory_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    material: Optional[Union[str, int]] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[Union[str, int]] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[Union[str, date]] = None
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: Optional[str] = "false"
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[str] = "false"
    returned_date: Optional[Union[str, date]] = None
    on_event: Optional[str] = "false"
    in_office: Optional[str] = "false"
    in_warehouse: Optional[str] = "false"
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    inventory_barcode: Optional[Union[str, int]] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None
    inventory_qrcode_url: Optional[str] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )

class InventoryRedisOut(StoreInventoryRedis):
    @classmethod
    def from_redis(cls, redis_data: str):
        data = json.loads(redis_data)
        return cls(**data)

class GoogleSyncInventoryBase(BaseValidators, BaseModel):
    id: Optional[str] = None
    product_id: Optional[str] = None  
    inventory_id: Optional[str] = None  
    sno: Optional[Union[str, int]] = None
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = 0
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[Union[str, date]] = Field(default=None, description="Purchase date in YYYY-MM-DD format")
    purchase_amount: Optional[Union[str, float, int]] = 0
    repair_quantity: Optional[Union[str, float, int]] = 0
    repair_cost: Optional[Union[str, float, int]] = 0
    on_rent: Optional[Union[str, bool]] = False
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = 0
    rented_inventory_returned: Optional[Union[str, bool]] = False
    returned_date: Optional[Union[str, date]] = Field(default=None, description="Return date in YYYY-MM-DD format")
    on_event: Optional[Union[str, bool]] = False
    in_office: Optional[Union[str, bool]] = False
    in_warehouse: Optional[Union[str, bool]] = False
    issued_qty: Optional[Union[str, float, int]] = 0
    balance_qty: Optional[Union[str, float, int]] = 0
    submitted_by: Optional[str] = "System Sync"
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    inventory_barcode: Optional[str] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None
    inventory_qrcode_url: Optional[str] = None

    model_config = ConfigDict(
        extra="ignore",
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )

class GoogleSyncInventoryCreate(GoogleSyncInventoryBase):
    model_config = ConfigDict(
        extra="ignore"
    )
