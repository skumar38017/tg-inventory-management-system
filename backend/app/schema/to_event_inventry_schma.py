# backend/app/schema/to_event_inventry_schma.py
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
import uuid
import json
import re
from enum import Enum

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class StatusEnum(str, Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class InventoryItemBase(BaseModel):
    zone_active: Optional[str] = None
    sno: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    material: Optional[str] = None
    comments: Optional[str] = None
    total: Optional[str] = None  # Matches String in SQLAlchemy model
    unit: Optional[str] = None
    per_unit_power: Optional[str] = None  # Matches String in SQLAlchemy model
    total_power: Optional[str] = None  # Matches String in SQLAlchemy model
    status: Optional[StatusEnum] = None
    poc: Optional[str] = None

    @field_validator('material', 'comments', mode='before')
    def empty_to_none(cls, v):
        return None if v == '' else v

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemOut(BaseModel):
    id: Optional[str] = None
    project_id: Optional[str] = None
    zone_active: Optional[str] = None
    sno: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    material: Optional[str] = None
    comments: Optional[str] = None
    total: Optional[str] = None
    unit: Optional[str] = None
    per_unit_power: Optional[str] = None
    total_power: Optional[str] = None
    status: Optional[StatusEnum] = None
    poc: Optional[str] = None

    @field_validator('id', mode='before')
    def set_id_from_uuid(cls, v, values):
        if v is None and 'uuid' in values:
            return values['uuid']
        return v
    
    @field_validator('project_id', mode='before')
    def format_project_id(cls, v):
        if v is None:
            raise ValueError("Project_id cannot be empty")
        clean_id = re.sub(r'^PRJ', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Project_id must contain only numbers after prefix")
        return f"PRJ{clean_id}"
        
    @field_validator('material', 'comments', mode='before')
    def empty_to_none(cls, v):
        return None if v == '' else v

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class ToEventInventoryBase(BaseModel):
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[date] = None
    project_name: Optional[str] = None
    event_date: Optional[date] = None
    submitted_by: Optional[str] = None
    inventory_items: List[InventoryItemBase]
    cretaed_at: datetime
    updated_at: datetime

    @field_validator('setup_date', 'event_date', mode='before')
    def parse_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                return datetime.fromisoformat(v).date()
        elif isinstance(v, datetime):
            return v.date()
        return v

    @field_validator('project_id', mode='before')
    def format_project_id(cls, v):
        if v is None:
            raise ValueError("Project_id cannot be empty")
        clean_id = re.sub(r'^PRJ', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Project_id must contain only numbers after prefix")
        return f"PRJ{clean_id}"
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class ToEventInventoryCreate(ToEventInventoryBase):
    model_config = ConfigDict(
        exclude={'id', 'created_at', 'updated_at'}
    )

class ToEventInventoryUpdate(BaseModel):
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[date] = None
    project_name: Optional[str] = None
    event_date: Optional[date] = None
    submitted_by: Optional[str] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None
    updated_at: datetime = datetime.now(timezone.utc)

    @field_validator('updated_at', mode='before')
    def set_timestamp(cls, v):
        return datetime.now(timezone.utc)
    
class ToEventInventoryOut(ToEventInventoryBase):
    id: Optional[str] = None
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[date] = None
    project_name: Optional[str] = None
    event_date: Optional[date] = None
    submitted_by: Optional[str] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None
    inventory_items: List[InventoryItemOut] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator('id', mode='before')
    def set_id_from_uuid(cls, v, values):
        if v is None and 'uuid' in values:
            return values['uuid']
        return v
    
    @field_validator('inventory_items', mode='before')
    def parse_inventory_items(cls, v):
        return [InventoryItemOut(**item) for item in v]
    
class ToEventInventoryUpdateOut(ToEventInventoryOut):
    updated_at: datetime

    @field_validator('updated_at', mode='before')
    def set_timestamp(cls, v):
        return datetime.now(timezone.utc)
    
    model_config = ConfigDict(from_attributes=True)
    
class ToEventInventorySearch(BaseModel):
    project_id: str
    
    @field_validator('project_id', mode='before')
    def format_project_id(cls, v):
        if v is None:
            raise ValueError("Project_id cannot be empty")
        clean_id = re.sub(r'^PRJ', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Project_id must contain only numbers after prefix")
        return f"PRJ{clean_id}"

class ToEventRedis(BaseModel):
    """Schema for storing inventory in Redis"""
    id: Optional[str] = None
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[date] = None
    project_name: Optional[str] = None
    event_date: Optional[date] = None
    submitted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None
    inventory_items: List[Dict[str, Any]] = []

    @field_validator('created_at', 'updated_at', mode='before')
    def parse_datetimes(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class ToEventRedisUpdate(BaseModel):
    """Schema for updating inventory in Redis"""
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[date] = None
    project_name: Optional[str] = None
    event_date: Optional[date] = None
    submitted_by: Optional[str] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None
    inventory_items: Optional[List[Dict[str, Any]]] = None
    updated_at: datetime = datetime.now(timezone.utc)

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class ToEventRedisOut(ToEventInventoryOut):
    """Schema for retrieving inventory from Redis"""
    pass
    