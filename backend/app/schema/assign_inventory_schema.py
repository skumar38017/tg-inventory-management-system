#  backend/app/schema/assign_inventory_schema

from pydantic import BaseModel, field_validator, ConfigDict, Field, model_validator
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
import uuid
import json
import re
from typing import Union
from enum import Enum
from pydantic import ValidationError


class StatusEnum(str, Enum):
    ASSIGNED = "assigned"
    RETURN = "returned"


class AssignmentInventoryBase(BaseModel):
    assign_to: Optional[str] = None
    employee_name: Optional[str] = None
    sno: Optional[str] = None
    zone_activity:  Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name:  Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[float, int, str]] = Field(None, ge=0)
    status: StatusEnum = Field(default=StatusEnum.ASSIGNED)
    purpose_reason:  Optional[str] = None
    assigned_date: Optional[date] = None
    assign_by:  Optional[str] = None
    comment: Optional[str] = None
 

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
                return float(v)
            except ValueError:
                raise ValueError("Quantity must be a number")
        return v

    @field_validator('assigned_date',  mode='before')
    def validate_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            StatusEnum: lambda v: v.value
        },
        extra='forbid'
    )


class AssignmentInventoryCreate(AssignmentInventoryBase):
    pass


class AssignmentInventoryOut(BaseModel):
    id: Optional[str]  = Field(None, frozen=True) 
    assign_to: Optional[str] = None
    inventory_id: Optional[str]  = Field(None, frozen=True) 
    project_id: Optional[str]  = Field(None, frozen=True) 
    product_id: Optional[str] = Field(None, frozen=True) 
    employee_name: Optional[str] = Field(None, frozen=True) 
    sno: Optional[str] = None
    zone_activity: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None
    status: Optional[StatusEnum] = None
    purpose_reason: Optional[str] = None
    assigned_date: Optional[date]  = Field(None, frozen=True) 
    submission_date: Optional[datetime] = None
    assign_by: Optional[str] = None
    comment: Optional[str] = None
    assignment_return_date: Optional[date] = None
    assignment_barcode:  Optional[str] = Field(None, frozen=True) 
    assignment_barcode_unique_code:  Optional[str]  = Field(None, frozen=True) 
    assignment_barcode_image_url: Optional[str] = Field(None, frozen=True) 
    
    
    created_at: Optional[datetime]  = Field(None, frozen=True) 
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
            StatusEnum: lambda v: v.value
        },
        extra='forbid'
    )


class AssignmentInventoryRedisIn(BaseModel):
    id: Optional[str] = None
    project_id: Optional[str] = None
    inventory_id: Optional[str] = None
    product_id: Optional[str] = None
    assign_to: Optional[str] = None
    employee_name: Optional[str] = None
    sno: Optional[str] = None
    zone_activity: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None
    status: Optional[StatusEnum] = None
    purpose_reason: Optional[str] = None
    assigned_date: Optional[date] = None
    submission_date: Optional[datetime] = None
    assign_by: Optional[str] = None
    comment: Optional[str] = None
    assignment_return_date: Optional[date] = None
    assignment_barcode:  Optional[str] = None
    assignment_barcode_unique_code:  Optional[str] = None
    assignment_barcode_image_url: Optional[str] = None
    
    crated_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class AssignmentInventoryRedisOut(AssignmentInventoryOut):
    pass

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
            StatusEnum: lambda v: v.value
        },
        extra='forbid'
    )

class AssignmentInventorySearch(BaseModel):
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

class AssignmentInventoryUpdate(BaseModel):
    # Search fields (required)
   
    # Updatable fields
    assign_to: Optional[str] = None
    sno: Optional[str] = None
    zone_activity: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[float, int, str]] = None
    status: Optional[StatusEnum] = None
    purpose_reason: Optional[str] = None
    assign_by: Optional[str] = None
    comment: Optional[str] = None
    submission_date: Optional[datetime] = None
    assigned_date: Optional[date]  = Field(None, frozen=True) 
    assignment_return_date: Optional[date] = None
       
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
        },
        extra='forbid'
    )

class AssignmentInventoryUpdateOut(AssignmentInventoryRedisOut):
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
    data: Union[AssignmentInventoryRedisOut,  Dict[str, Any]] 