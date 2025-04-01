#  backend/app/schema/entry_inventory_schema.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

# Pydantic schema for EntryInventory
class EntryInventoryBase(BaseModel):
    # Base schema without the 'uuid' and other auto-generated fields
    sno: Optional[str]
    inventory_id: str
    product_id: str
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

    # Automatically generated timestamps are typically not part of user input
    
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

    class Config:
        orm_mode = True  # Tells Pydantic to treat the SQLAlchemy model as a dict

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
    created_at: date
    updated_at: date

# Schema for creating or updating EntryInventory (without UUID and timestamps)
class EntryInventoryCreate(EntryInventoryBase):
    pass

# Schema for updating EntryInventory (includes only fields that can be updated)
class EntryInventoryUpdate(EntryInventoryBase):
    pass

#  Schema for Search EntryInventory (includes invetory_id and timestamp fields)
class EntryInventorySearch(EntryInventoryBase):
    pass

#  Schema for search date range filter
class DateRangeFilter(BaseModel):
    from_date: date
    to_date: date
    inventory_id: str

    class Config:
        orm_mode = True  # Tells Pydantic to treat the SQLAlchemy model as a dict

#  Schema for search date range filter
class SearchFilterOut(EntryInventoryBase):
    pass