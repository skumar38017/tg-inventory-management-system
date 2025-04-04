#  backend/app/schema/to_event_inventry_schma.py
from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, date, timezone
from typing import Optional
import re
from pydantic import validator
import json

class ToEventInventoryBase(BaseModel):
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date:  date
    project_name: Optional[str] = None
    event_date: date
    zone_active: Optional[str] = None
    sno: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    material: Optional[str] = None
    comments: Optional[str] = None
    total: Optional[str] = None
    unit: Optional[str] = None
    per_unit_power: Optional[str] = None
    total_power: Optional[str] = None
    status: Optional[str] = None
    poc: Optional[str] = None
    submitted_by: Optional[str] = None
 
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
        extra = "forbid"  # Strict validation
    
    @field_validator('project_id', mode='before')
    def format_product_id(cls, v):
        if v is None:
            raise ValueError("Product ID cannot be empty")
        clean_id = re.sub(r'^PRJ', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Product ID must contain only numbers after prefix")
        return f"PRJ{clean_id}"

    @field_validator('created_at', 'updated_at', mode='before')
    def set_timestamps(cls, v):
        return datetime.now(timezone.utc)  # Auto-set if not provided
    
    @field_validator('setup_date', 'event_date', mode='before')  # Corrected 'even_date' to 'event_date'
    def parse_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                return datetime.fromisoformat(v).date()
        elif isinstance(v, datetime):
            return v.date()
        return v
    
class ToEventInventoryCreate(ToEventInventoryBase):
    # Remove fields that should be auto-generated
    class Config:
        exclude = {'created_at', 'updated_at', 'uuid', 'project_barcode', 
                  'project_barcode_unique_code', 'project_barcode_image_url'}
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
 
class ToEventInventoryOut(ToEventInventoryBase):
    uuid: str
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date:  date
    project_name: Optional[str] = None
    event_date: date
    zone_active: Optional[str] = None
    sno: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    material: Optional[str] = None
    comments: Optional[str] = None
    total: Optional[str] = None
    unit: Optional[str] = None
    per_unit_power: Optional[str] = None
    total_power: Optional[str] = None
    status: Optional[str] = None
    poc: Optional[str] = None
    submitted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    bar_code: Optional[str] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None

    @validator('project_barcode_image_url', pre=True)
    def clean_barcode_url(cls, v):
        return v.replace('\"', '')
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()  # For pure date fields
        }

class ToEventInventoryUpload(ToEventInventoryOut):
    pass

class ToEventInventoryUpdate(BaseModel):
    employee_name: Optional[str] = None
    client_name: Optional[str] = None
    setup_date:  date
    project_name: Optional[str] = None
    event_date: date
    zone_active: Optional[str] = None
    sno: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    material: Optional[str] = None
    comments: Optional[str] = None
    total: Optional[str] = None
    unit: Optional[str] = None
    per_unit_power: Optional[str] = None
    total_power: Optional[str] = None
    status: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()  # For pure date fields
        }

    @field_validator('updated_at', mode='before')
    def set_timestamps(cls, v):
        return datetime.now(timezone.utc)  # Auto-set if not provided

class ToEventInventoryUpdateOut(ToEventInventoryOut):
    pass

# Schema to Store record in Redis after clicking {sync} button
class ToEventRedis(BaseModel):
    """Schema for storing inventory in Redis"""
    uuid: str
    sno: Optional[str] = None  # Changed to properly optional
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date:  date
    project_name: Optional[str] = None
    event_date: date
    zone_active: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    material: Optional[str] = None
    comments: Optional[str] = None
    total: Optional[str] = None
    unit: Optional[str] = None
    per_unit_power: Optional[str] = None
    total_power: Optional[str] = None
    status: Optional[str] = None
    poc: Optional[str] = None
    submitted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None  # Add this new field

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Schema to Show record from Redis after clicking {Show All} button
class ToEventRedisOut(BaseModel):
    """Schema for retrieving inventory from Redis"""
    uuid: str
    sno: Optional[str] = None  # Changed to properly optional
    project_id: Optional[str] = None
    employee_name: Optional[str] = None  
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date:  date
    project_name: Optional[str] = None
    event_date: date
    zone_active: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = None
    material: Optional[str] = None
    comments: Optional[str] = None
    total: Optional[str] = None
    unit: Optional[str] = None
    per_unit_power: Optional[str] = None
    total_power: Optional[str] = None
    status: Optional[str] = None
    poc: Optional[str] = None
    submitted_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None  # Add this new field

    @classmethod
    def from_redis(cls, redis_data: str):
        data = json.loads(redis_data)
        return cls(**data)
    
    @validator('project_barcode_image_url', pre=True)
    def empty_to_none(cls, v):
        return None if v == '' else v