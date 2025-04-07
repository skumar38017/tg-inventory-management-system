# backend/app/schema/to_event_inventry_schma.py
from pydantic import BaseModel, field_validator, ConfigDict, Field, model_validator
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

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )
    
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

    @field_validator('created_at', mode='before')
    def set_created_at(cls, v, values):
        # Set created_at only once when record is created (not updated)
        if v is None:
            return datetime.now(timezone.utc)
        return v

    @field_validator('updated_at', mode='before')
    def set_updated_at(cls, v, values):
        # Set updated_at every time the record is updated
        return datetime.now(timezone.utc)

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
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    cretaed_at: Optional[datetime] = None  # Explicitly include the typo field

    @model_validator(mode='before')
    def handle_timestamps(cls, values):
        # Handle the typo field
        if 'cretaed_at' in values and values['cretaed_at'] is not None:
            if 'created_at' not in values or values['created_at'] is None:
                values['created_at'] = values['cretaed_at']
        
        # Set defaults if still missing
        if 'created_at' not in values or values['created_at'] is None:
            values['created_at'] = datetime.now(timezone.utc)
        if 'updated_at' not in values or values['updated_at'] is None:
            values['updated_at'] = datetime.now(timezone.utc)
            
        return values
    
# ......................................................................................................
class RedisInventoryItem(BaseModel):
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
    id: Optional[str] = None
    project_id: Optional[str] = None

    @field_validator('project_id', mode='before')
    def format_project_id(cls, v):
        if v is None:
            return None
        clean_id = re.sub(r'^PRJ', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Project_id must contain only numbers after prefix")
        return f"PRJ{clean_id}"

    @field_validator('material', 'comments', mode='before')
    def empty_to_none(cls, v):
        return None if v == '' else v


class ToEventUploadSchema(BaseModel):
    id: Optional[str] = None
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[date] = None
    project_name: Optional[str] = None
    event_date: Optional[date] = None
    submitted_by: Optional[str] = None
    inventory_items: List[RedisInventoryItem]=[]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None

    # Handle the 'cretaed_at' typo in Redis data
    @field_validator('created_at', 'updated_at', mode='before')
    def handle_created_at_typo(cls, v, values):
        if v is None and 'cretaed_at' in values.data:
            return values.data['cretaed_at']
        return v

    @field_validator('project_id', mode='before')
    def format_project_id(cls, v):
        if v is None:
            raise ValueError("Project_id cannot be empty")
        clean_id = re.sub(r'^PRJ', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Project_id must contain only numbers after prefix")
        return f"PRJ{clean_id}"
    
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

    @field_validator('project_barcode_image_url', mode='before')
    def empty_url_to_none(cls, v):
        return None if v == '' else v

    def to_orm_dict(self):
        """Convert to dictionary suitable for SQLAlchemy model"""
        data = self.model_dump(exclude={'inventory_items', 'created_at', 'updated_at'})
        data['items'] = [item.model_dump(exclude={'project_id'}) for item in self.inventory_items]
        return data


class ToEventUploadResponse(BaseModel):
    success: bool
    message: str
    project_id: str
    inventory_items_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    cretaed_at: Optional[datetime] = None  # Keep for backward compatibility

    @model_validator(mode='before')
    def handle_timestamps(cls, data: dict) -> dict:
        now = datetime.now(timezone.utc)
        
        # Handle the typo field first
        if 'cretaed_at' in data and data['cretaed_at'] is not None:
            if data.get('created_at') is None:
                data['created_at'] = data['cretaed_at']
        
        # Ensure we have values for required timestamps
        if data.get('created_at') is None:
            data['created_at'] = now
        if data.get('updated_at') is None:
            data['updated_at'] = now
            
        # Clean up the typo field if it's None
        if 'cretaed_at' in data and data['cretaed_at'] is None:
            del data['cretaed_at']
            
        return data

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
        },
        extra='ignore'  # Ignore extra fields in response
    )
