#  backend/app/schema/entry_inventory_schema.py
from pydantic import BaseModel, field_validator, ConfigDict, Field, model_validator
from datetime import datetime, date, timezone
from typing import Optional, Dict
import re
import json
from typing import Union
from enum import Enum
from backend.app.utils.date_utils import UTCDateUtils
from backend.app.utils.field_validators import BaseValidators

class EntryInventoryBase(BaseValidators,BaseModel):
    product_id: Optional[str] = None  
    inventory_id: Optional[str] = None  
    sno: Optional[str] = None
    inventory_name: Optional[str] = None
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
        extra="forbid",
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )
    @field_validator('purchase_date', 'returned_date', mode='before')
    def parse_date_fields(cls, value):
        if value in [None, "", "null", "n/a", "N/A"]:
            return None
        if isinstance(value, date):
            return value
        try:
            return UTCDateUtils.parse_date(value)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format or null/n/a")
        
# Schema for creating or updating EntryInventory (without id and timestamps)
class EntryInventoryCreate(EntryInventoryBase):
    model_config = ConfigDict(
        exclude={'created_at', 'updated_at', 'id', 'bar_code'}
    )

class EntryInventoryOut(EntryInventoryBase):
    id: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    inventory_barcode: Optional[str] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils .format_date(v)
        }
    )
    
class EntryInventoryUpdate(BaseValidators, BaseModel):
    """Schema for updating inventory items"""
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
    
    @field_validator('purchase_date', 'returned_date', mode='before')
    def parse_date_fields(cls, value):
        if value in [None, "", "null", "n/a", "N/A"]:
            return None
        if isinstance(value, date):
            return value
        try:
            return UTCDateUtils.parse_date(value)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format or null/n/a")
        
class EntryInventoryUpdateOut(EntryInventoryOut):
    pass
        
# Schema for Search EntryInventory (includes invetory_id and timestamp fields)
class EntryInventorySearch(BaseValidators, BaseModel):
    """Schema for searching inventory items"""
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
class DateRangeFilter(BaseModel):
    """Schema for date range filtering"""
    from_date: Union[str, date]
    to_date: Union[str, date]

    @model_validator(mode='after')
    def validate_date_range(self) -> 'DateRangeFilter':
        if self.to_date < self.from_date:
            raise ValueError("To date must be after From date")
        return self

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )

class DateRangeFilterOut(EntryInventoryOut):
    pass

# Schema for sync inventory
class SyncInventoryOut(EntryInventoryOut):
    pass

# Schema for Store record in Redis after clicking {sync} button
class StoreInventoryRedis(BaseModel, BaseValidators):
    """Schema for storing inventory in Redis"""
    id: Optional[Union[str, int]] = None
    sno: Optional[Union[str, int]] = None  # Changed to properly optional
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
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    returned_date: Optional[Union[str, date]] = None
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    inventory_barcode: Optional[Union[str, int]] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )

# Schema to Show record from Redis after clicking {Show All} button
class InventoryRedisOut(StoreInventoryRedis):
    """Redis output model"""
    @classmethod
    def from_redis(cls, redis_data: str):
        data = json.loads(redis_data)
        return cls(**data)

class GoogleSyncInventoryBase(BaseValidators, BaseModel):
    id: Optional[str] = None  # Allow id in base model
    product_id: Optional[str] = None  
    inventory_id: Optional[str] = None  
    sno: Optional[Union[str, int]] = None  # Accept both string and int
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = 0  # Default to 0
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[Union[str, date]] = Field(default=None, description="Purchase date in YYYY-MM-DD format")
    purchase_amount: Optional[Union[str, float, int]] = 0
    repair_quantity: Optional[Union[str, float, int]] = 0  # Default to 0
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
    created_at: Optional[Union[str, datetime]] = None  # Allow updated_at
    updated_at: Optional[Union[str, datetime]] = None  # Allow updated_at
    inventory_barcode: Optional[str] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None

    model_config = ConfigDict(
        extra="ignore",
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )

    @field_validator('sno', mode='before')
    def convert_sno_to_string(cls, v):
        if v is None:
            return None
        return str(v)

    @field_validator('purchase_date', 'returned_date', mode='before')
    def parse_date_fields(cls, value):
        if value in [None, "", "null", "n/a", "N/A", "yyyy-mm-dd", "YYYY-MM-DD"]:
            return None  # Return None instead of string
        if isinstance(value, date):
            return value
        try:
            return UTCDateUtils.parse_date(value)
        except ValueError:
            return None  # Return None on parse failure

class GoogleSyncInventoryCreate(GoogleSyncInventoryBase):
    model_config = ConfigDict(
        # No longer excluding fields since we want to allow them
        extra="ignore"
    )

class EntryInventoryBarcodeOut(BaseValidators, BaseModel):
    company: Optional[str] = "Tagglabs Experiential PVT. LTD.",
    address: Optional[str] = "Eros City Square Mall, Eros City Square, Eros City, Haryana, India",
    product_id: Optional[str] = None  
    inventory_id: Optional[str] = None  
    sno: Optional[Union[str, int]] = None
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    purchase_date: Optional[Union[str, date]] = None
    on_rent: Optional[str] = "false" 
    vendor_name: Optional[str] = None
    rented_inventory_returned: Optional[str] = "false" 
    returned_date: Optional[Union[str, date]] = None 
    on_event: Optional[str] = "false"  
    in_office: Optional[str] = "false"  
    in_warehouse: Optional[str] = "false"  
    submitted_by: Optional[str] = "Inventory Administator"
    created_at: Optional[Union[str, datetime]] = None
    inventory_barcode_url: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )