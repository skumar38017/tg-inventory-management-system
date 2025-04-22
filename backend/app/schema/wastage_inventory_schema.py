#  backend/app/schema/wastage_inventory_schema

from pydantic import BaseModel, field_validator, ConfigDict, Field
from datetime import datetime, date, timezone
from typing import Optional, Union, Dict, Any, List
import uuid
import json
import re
from typing import Union
from enum import Enum
from pydantic import ValidationError
from backend.app.schema.entry_inventory_schema import EntryInventoryOut, InventoryRedisOut
from backend.app.schema.to_event_inventry_schma import ToEventRedisOut, ToEventInventoryOut, ToEventRedisUpdateOut, InventoryItemOut
from backend.app.schema.assign_inventory_schema import AssignmentInventoryRedisOut
from backend.app.models.wastege_inventory_model import WastageInventory

class WastageInventoryBase(BaseModel):
    assign_to: Optional[str] = None
    sno: Optional[str] = None
    employee_name: Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, int]] = None
    status: Optional[str] = None
    receive_date: Optional[Union[date, str]] = None
    receive_by: Optional[str] = None
    check_status: Optional[str] = None
    location: Optional[str] = None
    project_name: Optional[str] = None
    event_date: Optional[Union[date, str]] = None
    comment: Optional[str] = None
    zone_activity: Optional[str] = None
    
    # Wastage specific fields
    wastage_reason: Optional[str] = None
    wastage_date: Optional[Union[date, str]] = None
    wastage_approved_by: Optional[str] = None
    wastage_status: Optional[str] = None

    @field_validator('inventory_id', mode='before')
    def format_inventory_id(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        if not v.startswith('INV'):
            return f"INV{v}"
        return v

    @field_validator('project_id', mode='before')
    def format_project_id(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        if not v.startswith('PRJ'):
            return f"PRJ{v}"
        return v

    @field_validator('product_id', mode='before')
    def format_product_id(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        if not v.startswith('PRD'):
            return f"PRD{v}"
        return v

    @field_validator('quantity', mode='before')
    def validate_quantity(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            if not v.strip():
                return None
            try:
                return int(float(v))
            except ValueError:
                raise ValueError("Quantity must be a whole number")
        elif isinstance(v, (float, int)):
            return int(v)
        return v

    @field_validator('receive_date', 'event_date', 'wastage_date', mode='before')
    def validate_dates(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        elif isinstance(v, datetime):
            return v.date()
        return v
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        },
        extra='forbid'
    )

class WastageInventoryCreate(WastageInventoryBase):
    pass

class WastageInventoryOut(BaseModel):
    id: Optional[str]  = Field(None, frozen=True) 
    assign_to: Optional[str] = None
    sno: Optional[str] = None
    employee_name: Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, int]] = None
    status: Optional[str] = None
    receive_date: Optional[Union[date, str]] = None
    receive_by: Optional[str] = None
    check_status: Optional[str] = None
    location: Optional[str] = None
    project_name: Optional[str] = None
    event_date: Optional[Union[date, str]] = None
    comment: Optional[str] = None
    zone_activity: Optional[str] = None
    wastage_barcode:  Optional[str] = Field(None, frozen=True) 
    wastage_barcode_image_url: Optional[str] = Field(None, frozen=True) 
    
    # Wastage specific fields
    wastage_reason: Optional[str] = None
    wastage_date: Optional[Union[date, str]] = None
    wastage_approved_by: Optional[str] = None
    wastage_status: Optional[str] = None
    
    created_at: Optional[Union[datetime, str]]  = Field(None, frozen=True) 
    updated_at: Optional[Union[datetime, str]] = None

    @field_validator('updated_at', 'created_at', mode='before')
    def parse_datetime(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # Parse and make timezone-naive for consistent comparison
                return datetime.fromisoformat(value).replace(tzinfo=None)
            except ValueError:
                return None
        elif isinstance(value, datetime):
            return value.replace(tzinfo=None)
        return value
    
    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        },
        extra='ignore'
    )

class WastageInventoryRedisIn(BaseModel):
    id: Optional[str]  = Field(None, frozen=True) 
    assign_to: Optional[str] = None
    sno: Optional[str] = None
    employee_name: Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, int]] = None
    status: Optional[str] = None
    receive_date: Optional[Union[date, str]] = None
    receive_by: Optional[str] = None
    check_status: Optional[str] = None
    location: Optional[str] = None
    project_name: Optional[str] = None
    event_date: Optional[date]  = Field(None, frozen=True) 
    comment: Optional[str] = None
    zone_activity: Optional[str] = None
    wastage_barcode:  Optional[str] = Field(None, frozen=True) 
    wastage_barcode_unique_code:  Optional[str]  = Field(None, frozen=True) 
    wastage_barcode_image_url: Optional[str] = Field(None, frozen=True) 
    
    # Wastage specific fields
    wastage_reason: Optional[str] = None
    wastage_date: Optional[Union[date, str]] = None
    wastage_approved_by: Optional[str] = None
    wastage_status: Optional[str] = None
    
    created_at: Optional[Union[datetime, str]]  = Field(None, frozen=True) 
    updated_at: Optional[Union[datetime, str]] = None

    @field_validator('receive_date', 'event_date', 'wastage_date', mode='before')
    def validate_dates(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                # Parse date string and return date object
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        elif isinstance(v, datetime):
            return v.date()
        return v

    @field_validator('created_at', 'updated_at', mode='before')
    def parse_datetime(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # Parse ISO format string
                return datetime.fromisoformat(value).replace(tzinfo=None)
            except ValueError:
                return None
        elif isinstance(value, datetime):
            return value.replace(tzinfo=None)
        return value

class WastageInventoryRedisOut(WastageInventoryOut):
    success: Optional[bool] = Field(None, exclude=True) 
    message: Optional[str] = Field(None, exclude=True)  
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
        },
        extra='ignore'
    )

class WastageInventorySearch(BaseModel):
    employee_name: Optional[str] = None
    inventory_id: Optional[str] = None

    @field_validator('inventory_id', mode='before')
    def format_inventory_id(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        if not v.startswith('INV'):
            return f"INV{v}"
        return v

class WastageInventoryUpdate(BaseModel):
    assign_to: Optional[str] = None
    sno: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, int]] = None
    status: Optional[str] = None
    receive_date: Optional[Union[date, str]] = None
    receive_by: Optional[str] = None
    check_status: Optional[str] = None
    location: Optional[str] = None
    project_name: Optional[str] = Field(None, frozen=True) 
    comment: Optional[str] = None
    zone_activity: Optional[str] = None
    
    # Wastage specific fields
    wastage_reason: Optional[str] = None
    wastage_date: Optional[Union[date, str]] = None
    wastage_approved_by: Optional[str] = None
    wastage_status: Optional[str] = None
    updated_at: Optional[Union[datetime, str]] = None
       
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
        },
        extra='forbid'
    )

class WastageInventoryUpdateOut(WastageInventoryRedisOut):
    pass

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
        },
        extra='forbid'
    )

class RedisSearchResult(BaseModel):
    key: str
    data: Union[
        AssignmentInventoryRedisOut, 
        ToEventInventoryOut,
        ToEventRedisUpdateOut,
        InventoryItemOut,
        ToEventRedisOut, 
        InventoryRedisOut, 
        EntryInventoryOut,
        Dict[str, Any]
    ]
    
    model_config = ConfigDict(
        extra="allow"
    )

