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
    assignment_return_date: Optional[date] = None    

    @field_validator('inventory_id',  mode='before')
    def validate_inventory_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            if not re.fullmatch(r'INV\d+', v):
                raise ValueError("Project ID must be in format PRJ followed by numbers")
        return v

    @field_validator('project_id', mode='before')
    def validate_project_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            if not re.fullmatch(r'PRJ\d+', v):
                raise ValueError("Project ID must be in format PRJ followed by numbers")
        return v

    @field_validator('product_id', mode='before')
    def validate_product_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            if not re.fullmatch(r'PRD\d+', v):
                raise ValueError("Product ID must be in format PRD followed by numbers")
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

    @field_validator('assigned_date', 'assignment_return_date', mode='before')
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
    id: Optional[str] = None
    assign_to: Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
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
    
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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


class AssignmentInventoryRedisOut(AssignmentInventoryOut):
    pass


class AssignmentInventorySearch(BaseModel):
    employee_name: Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None

    @field_validator('inventory_id',  mode='before')
    def validate_inventory_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            if not re.fullmatch(r'INV\d+', v):
                raise ValueError("Project ID must be in format PRJ followed by numbers")
        return v

    @field_validator('project_id', mode='before')
    def validate_project_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            if not re.fullmatch(r'PRJ\d+', v):
                raise ValueError("Project ID must be in format PRJ followed by numbers")
        return v

    @field_validator('product_id', mode='before')
    def validate_product_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            if not re.fullmatch(r'PRD\d+', v):
                raise ValueError("Product ID must be in format PRD followed by numbers")
        return v


class AssignmentInventoryUpdate(BaseModel):  # Renamed to avoid conflict
    inventory_id: Optional[str] = None
    employee_name: Optional[str] = None
    sno: Optional[str] = None
    zone_activity: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None
    status: Optional[StatusEnum] = None
    purpose_reason: Optional[str] = None
    assign_by: Optional[str] = None
    comment: Optional[str] = None
    assignment_return_date: Optional[date] = None
    updated_at: Optional[datetime] = None


class AssignmentInventoryUpdateOut(AssignmentInventoryRedisOut):
    pass
