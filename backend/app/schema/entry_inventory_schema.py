#  backend/app/schema/entry_inventory_schema.py
from pydantic import BaseModel, field_validator
from datetime import datetime, date, timezone
from typing import Optional
import re
import json

class EntryInventoryBase(BaseModel):
    product_id: str  
    inventory_id: str  

    sno: Optional[str] = None
    name: str
    material: str
    total_quantity: str
    manufacturer: str
    purchase_dealer: str
    purchase_date: date
    purchase_amount: str
    repair_quantity: Optional[str] = None
    repair_cost: Optional[str] = None
    on_rent: str
    vendor_name: str
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = None
    returned_date: Optional[date] = None
    on_event: str
    in_office: str
    in_warehouse: str
    issued_qty: str
    balance_qty: str
    submitted_by: str

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # These fields shouldn't be in the create schema since they're auto-generated

    class Config:
        from_attributes = True  # For Pydantic v2 (replaces orm_mode)
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Ensure proper JSON serialization
        } # Treat SQLAlchemy model as a dict

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

# Schema for reading EntryInventory (includes inventory_id and timestamp fields)
class EntryInventoryOut(EntryInventoryBase):
    uuid: str
    sno: str
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
    on_rent: str
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = None
    returned_date: Optional[date] = None
    on_event: str
    in_office: str
    in_warehouse: str
    issued_qty: str
    balance_qty: str
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    bar_code: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()  # For pure date fields
        }  # For Pydantic v2 compatibility

# Schema for creating or updating EntryInventory (without UUID and timestamps)
class EntryInventoryCreate(EntryInventoryBase):
    @field_validator('created_at', mode='before')
    def set_created_at(cls, v):
        return v or datetime.now(timezone.utc)
    

class EntryInventoryUpdate(BaseModel):
    name: str
    material: str
    total_quantity: str
    manufacturer: str
    purchase_dealer: str
    purchase_date: date
    purchase_amount: str
    repair_quantity: Optional[str] = None
    repair_cost: Optional[str] = None
    on_rent: str
    vendor_name: str
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = None
    returned_date: Optional[date] = None
    on_event: str
    in_office: str
    in_warehouse: str
    issued_qty: str
    balance_qty: str
    submitted_by: str
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
    uuid: str
    sno: str
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
    on_rent: str
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = None
    returned_date: Optional[date] = None
    on_event: str
    in_office: str
    in_warehouse: str
    issued_qty: str
    balance_qty: str
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    bar_code: str

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()  # For pure date fields
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
    sno: Optional[str] = None 
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
    on_rent: str
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = None
    returned_date: Optional[date] = None
    on_event: str
    in_office: str
    in_warehouse: str
    issued_qty: str
    balance_qty: str
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    bar_code: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Schema to Show record from Redis after clicking {Show All} button
class InventoryRedisOut(BaseModel):
    """Schema for retrieving inventory from Redis"""

    uuid: str
    sno: Optional[str] = None 
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
    on_rent: str
    vendor_name: Optional[str] = None
    total_rent: Optional[str] = None
    rented_inventory_returned: Optional[str] = None
    returned_date: Optional[date] = None
    on_event: str
    in_office: str
    in_warehouse: str
    issued_qty: str
    balance_qty: str
    submitted_by: str
    created_at: datetime
    updated_at: datetime
    bar_code: str

    @classmethod
    def from_redis(cls, redis_data: str):
        data = json.loads(redis_data)
        return cls(**data)