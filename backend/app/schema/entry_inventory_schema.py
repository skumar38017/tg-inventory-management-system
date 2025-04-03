#  backend/app/schema/entry_inventory_schema.py
from pydantic import BaseModel, field_validator
from datetime import datetime, date, timezone
from typing import Optional
import re
from pydantic import validator
import json
 
class EntryInventoryBase(BaseModel):
    product_id: str  
    inventory_id: str  
    sno: Optional[str] = None
    name: str
    material: Optional[str] = None
    total_quantity: str
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[str] = None
    repair_quantity: Optional[str] = None
    repair_cost: Optional[str] = None
    on_rent: str = "false"  # Changed to non-optional with default
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: str = "false"  # Changed to non-optional with default
    returned_date: Optional[date] = None  # Added this missing field
    on_event: str = "false"  # Changed to non-optional with default
    in_office: str = "false"  # Changed to non-optional with default
    in_warehouse: str = "false"  # Changed to non-optional with default
    issued_qty: Optional[str] = None
    balance_qty: Optional[str] = None
    submitted_by: str

    # These should NOT be in the create schema
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
    
    @field_validator('created_at', 'updated_at', mode='before')
    def set_timestamps(cls, v):
        return datetime.now(timezone.utc)  # Auto-set if not provided
    
# Schema for creating or updating EntryInventory (without UUID and timestamps)
class EntryInventoryCreate(EntryInventoryBase):
    # Remove fields that should be auto-generated
    class Config:
        exclude = {'created_at', 'updated_at', 'uuid', 'bar_code'}
        
    @validator('on_rent', 'rented_inventory_returned', 'on_event', 'in_office', 'in_warehouse', pre=True)
    def validate_booleans(cls, v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return v.lower()
        return "false"

# Schema for reading EntryInventory (includes inventory_id and timestamp fields)
class EntryInventoryOut(EntryInventoryBase):
    uuid: str
    product_id: str  
    inventory_id: str  
    sno: Optional[str] = None
    name: str
    material: Optional[str] = None
    total_quantity: str
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[str] = None
    repair_quantity: Optional[str] = None
    repair_cost: Optional[str] = None
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[str] = None
    balance_qty: Optional[str] = None
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    bar_code: str
    barcode_image_url: Optional[str] = None  # Add this new field

    @validator('barcode_image_url', pre=True)
    def clean_barcode_url(cls, v):
        return v.replace('\"', '')
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()  # For pure date fields
        } # For Pydantic v2 compatibility
   
class EntryInventoryUpdate(BaseModel):
    name: str
    material: Optional[str] = None
    total_quantity: str
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[str] = None
    repair_quantity: Optional[str] = None
    repair_cost: Optional[str] = None
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[str] = None
    balance_qty: Optional[str] = None
    submitted_by: str
    submitted_by: str
    updated_at: datetime

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
    uuid: str
    product_id: str  
    inventory_id: str  
    sno: Optional[str] = None
    name: str
    material: Optional[str] = None
    total_quantity: str
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[str] = None
    repair_quantity: Optional[str] = None
    repair_cost: Optional[str] = None
    on_rent: Optional[str] = "false"
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = "false"
    on_event: Optional[str] = "false"
    in_office: Optional[str] = "false"
    in_warehouse: Optional[str] = "false"
    issued_qty: Optional[str] = None
    balance_qty: Optional[str] = None
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    barcode_image_url: Optional[str] = None  # Add this new field
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

# Schema for Search EntryInventory (includes invetory_id and timestamp fields)
class EntryInventorySearch(EntryInventoryBase):
    pass

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
    uuid: str
    sno: Optional[str] = None  # Changed to properly optional
    inventory_id: str
    product_id: str
    name: str
    material: Optional[str] = None
    total_quantity: str
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[str] = None
    repair_quantity: Optional[str] = None
    repair_cost: Optional[str] = None
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[str] = None
    balance_qty: Optional[str] = None
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    bar_code: str
    barcode_image_url: Optional[str] = None  # Add this new field

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Schema to Show record from Redis after clicking {Show All} button
class InventoryRedisOut(BaseModel):
    """Schema for retrieving inventory from Redis"""

    uuid: str
    sno: Optional[str] = None  # Changed to properly optional
    inventory_id: str
    product_id: str
    name: str
    material: Optional[str] = None
    total_quantity: str
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_amount: Optional[str] = None
    repair_quantity: Optional[str] = None
    repair_cost: Optional[str] = None
    on_rent: Optional[str] = "false"  # Default value
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = "false"  # Default value
    on_event: Optional[str] = "false"  # Default value
    in_office: Optional[str] = "false"  # Default value
    in_warehouse: Optional[str] = "false"  # Default value
    issued_qty: Optional[str] = None
    balance_qty: Optional[str] = None
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    barcode_image_url: Optional[str] = None  # Add this new field

    @classmethod
    def from_redis(cls, redis_data: str):
        data = json.loads(redis_data)
        return cls(**data)