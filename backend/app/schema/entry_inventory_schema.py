#  backend/app/schema/entry_inventory_schema.py
from pydantic import BaseModel, field_validator, validator
from datetime import datetime, date, timezone
from typing import Optional
import re
import json
from typing import Union
from enum import Enum
 
class EntryInventoryBase(BaseModel):
    product_id: Optional[str] = None  
    inventory_id: Optional[str] = None  
    sno: Optional[str] = None
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: str = "false"  # Changed to non-optional with default
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: str = "false"  # Changed to non-optional with default
    returned_date: Optional[date] = None  # Added this missing field
    on_event: str = "false"  # Changed to non-optional with default
    in_office: str = "false"  # Changed to non-optional with default
    in_warehouse: str = "false"  # Changed to non-optional with default
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None

    # These fields shouldn't be in the create schema since they're auto-generated

    class Config:
        extra = "forbid"  # Strict validation
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    
    @field_validator('product_id', mode='before')
    def format_product_id(cls, v):
        if v is None:
            raise ValueError("Product ID cannot be empty")
        clean_id = re.sub(r'^PRD', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Product ID must contain only numbers after prefix")
        return f"PRD{clean_id}"

    @field_validator('inventory_id', mode='before')
    def format_inventory_id(cls, v):
        if v is None:
            raise ValueError("Inventory ID cannot be empty")
        clean_id = re.sub(r'^INV', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Inventory ID must contain only numbers after prefix")
        return f"INV{clean_id}"
    
# Schema for creating or updating EntryInventory (without id and timestamps)
class EntryInventoryCreate(EntryInventoryBase):
    # Remove fields that should be auto-generated
    class Config:
        exclude = {'created_at', 'updated_at', 'id', 'bar_code'}
        
    @validator('on_rent', 'rented_inventory_returned', 'on_event', 'in_office', 'in_warehouse', pre=True)
    def validate_booleans(cls, v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return v.lower()
        return "false"

# Schema for reading EntryInventory (includes inventory_id and timestamp fields)
class EntryInventoryOut(EntryInventoryBase):
    id: Optional[str] = None
    product_id: Optional[str] = None  
    inventory_id: Optional[str] = None  
    sno: Optional[str] = None
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    inventory_barcode: Optional[str] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None

    @validator('inventory_barcode_url', pre=True)
    def clean_barcode_url(cls, v):
        return v.replace('\"', '')
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()  # For pure date fields
        } # For Pydantic v2 compatibility
   
class EntryInventoryUpdate(BaseModel):
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None
    submitted_by: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @field_validator('updated_at', mode='before')
    def set_updated_at(cls, v):
        return datetime.now(timezone.utc)
    
class EntryInventoryUpdateOut(EntryInventoryBase):
    pass
    
class EntryInventoryOut(EntryInventoryBase):
    id: Optional[str] = None
    product_id: Optional[str] = None  
    inventory_id: Optional[str] = None  
    sno: Optional[str] = None
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: Optional[str] = "false"
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[str] = "false"
    on_event: Optional[str] = "false"
    in_office: Optional[str] = "false"
    in_warehouse: Optional[str] = "false"
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    inventory_barcode: Optional[str] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

# Schema for Search EntryInventory (includes invetory_id and timestamp fields)
class EntryInventorySearch(BaseModel):
    """Schema for searching inventory items"""
    inventory_id: Optional[str] = None
    product_id: Optional[str] = None
    project_id: Optional[str] = None


    @field_validator('*')
    def check_empty_strings(cls, v):
        if v == "":
            return None
        return v

    class Config:
        extra = "forbid"  # Prevent extra fields

# Schema for search date range filter
class DateRangeFilter(BaseModel):
    from_date: date
    to_date: date

    @field_validator('to_date')
    def validate_dates(cls, v: date, info) -> date:
        if hasattr(info, 'data') and 'from_date' in info.data and v < info.data['from_date']:
            raise ValueError("To date must be after From date")
        return v

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class DateRangeFilterOut(EntryInventoryBase):
    pass

# Schema for sync inventory
class SyncInventoryOut(EntryInventoryBase):
    pass

# Schema for Store record in Redis after clicking {sync} button
class StoreInventoryRedis(BaseModel):
    """Schema for storing inventory in Redis"""
    id: Optional[str] = None
    sno: Optional[str] = None  # Changed to properly optional
    inventory_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    inventory_barcode: Optional[str] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

# Schema to Show record from Redis after clicking {Show All} button
class InventoryRedisOut(BaseModel):
    """Schema for retrieving inventory from Redis"""

    id: Optional[str] = None
    sno: Optional[str] = None  # Changed to properly optional
    inventory_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    total_quantity: Optional[Union[str, float, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    repair_cost: Optional[Union[str, float, int]] = None
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, float, int]] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[Union[str, float, int]] = None
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    inventory_barcode: Optional[str] = None
    inventory_unique_code: Optional[str] = None
    inventory_barcode_url: Optional[str] = None

    @classmethod
    def from_redis(cls, redis_data: str):
        data = json.loads(redis_data)
        return cls(**data)