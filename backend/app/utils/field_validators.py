# backend/app/validations/inventory_validations.py
import re
from datetime import datetime, date, timezone
from typing import Optional, Union, Dict, Any
from enum import Enum
from pydantic import field_validator, model_validator, validator, ValidationInfo

# ---------------------------- Common Enums ----------------------------
class AssignmentStatusEnum(str, Enum):
    ASSIGNED = "assigned"
    RETURN = "returned"

class EventStatusEnum(str, Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    INHOUSE = "In House"
    OUTSIDE = "Outside"
    PURCHASED = "Purchased"
    RETURNED = "Returned"
    REJECTED = "Rejected"
    PENDING = "Pending"
    FAILED = "Failed"
    APPROVED = "Approved"
    UNDER_REVIEW = "Under Review"
    ON_HOLD = "On Hold"
    DELIVERED = "Delivered"
    SHIPPED = "Shipped"
    IN_TRANSIT = "In Transit"
    DELAYED = "Delayed"
    CLOSED = "Closed"
    OPEN = "Open"
    EXPIRED = "Expired"
    WITHDRAWN = "Withdrawn"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    RESERVED = "Reserved"
    WAITLISTED = "Waitlisted"
    IN_HOUSE = "In House"

# ---------------------------- Shared Validators ----------------------------
class BaseValidators:
    """Contains validators that can be reused across different schemas"""
    
    @staticmethod
    def format_id_field(v: Optional[str], prefix: str) -> Optional[str]:
        """Generic ID formatter that adds prefix if missing"""
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        if not v.startswith(prefix):
            return f"{prefix}{v}"
        return v

    @staticmethod
    def validate_date_field(v) -> Optional[date]:
        """Parse date from string or datetime object"""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                try:
                    return datetime.fromisoformat(v).date()
                except ValueError:
                    raise ValueError("Date must be in YYYY-MM-DD format")
        elif isinstance(v, datetime):
            return v.date()
        return v

    @staticmethod
    def validate_quantity(v) -> Optional[Union[float, int]]:
        """Convert quantity to number, handling strings and empty values"""
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

    @staticmethod
    def empty_string_to_none(v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None"""
        return None if v == '' else v

    @staticmethod
    def convert_to_string(v) -> Optional[str]:
        """Convert value to string if it isn't already"""
        if v is None:
            return None
        return str(v) if not isinstance(v, str) else v

    @staticmethod
    def handle_created_at_typo(v, values: Dict) -> datetime:
        """Handle common 'cretaed_at' typo in timestamp fields"""
        if v is None and 'cretaed_at' in values:
            return values['cretaed_at']
        return v or datetime.now(timezone.utc)

# ---------------------------- Schema-Specific Validators ----------------------------
class AssignmentInventoryValidations(BaseValidators):
    """Validators specific to assignment inventory"""
    
    @field_validator('inventory_id', mode='before')
    def validate_inventory_id(cls, v):
        return cls.format_id_field(v, 'INV')

    @field_validator('project_id', mode='before')
    def validate_project_id(cls, v):
        return cls.format_id_field(v, 'PRJ')

    @field_validator('product_id', mode='before')
    def validate_product_id(cls, v):
        return cls.format_id_field(v, 'PRD')

    @field_validator('assigned_date', 'assignment_return_date', mode='before')
    def validate_assignment_dates(cls, v):
        return cls.validate_date_field(v)

class EntryInventoryValidations(BaseValidators):
    """Validators specific to entry inventory"""
    
    @field_validator('product_id', mode='before')
    def validate_product_id(cls, v):
        if v is None:
            raise ValueError("Product ID cannot be empty")
        clean_id = re.sub(r'^PRD', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Product ID must contain only numbers after prefix")
        return f"PRD{clean_id}"

    @field_validator('inventory_id', mode='before')
    def validate_inventory_id(cls, v):
        if v is None:
            raise ValueError("Inventory ID cannot be empty")
        clean_id = re.sub(r'^INV', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Inventory ID must contain only numbers after prefix")
        return f"INV{clean_id}"
    
    @validator('on_rent', 'rented_inventory_returned', 'on_event', 'in_office', 'in_warehouse', pre=True)
    def validate_boolean_fields(cls, v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return v.lower()
        return "false"

    @field_validator('barcode_image_url', pre=True)
    def clean_barcode_url(cls, v):
        return cls.empty_string_to_none(v.replace('\"', ''))

class ToEventInventoryValidations(BaseValidators):
    """Validators specific to event inventory"""
    
    @field_validator('project_id', mode='before')
    def validate_project_id(cls, v):
        if v is None:
            raise ValueError("Project_id cannot be empty")
        clean_id = re.sub(r'^PRJ', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Project_id must contain only numbers after prefix")
        return f"PRJ{clean_id}"

    @model_validator(mode='before')
    def handle_event_timestamps(cls, values: Dict) -> Dict:
        """Special handling for event timestamps including typo correction"""
        if not isinstance(values, dict):
            return values
            
        values['created_at'] = cls.handle_created_at_typo(
            values.get('created_at'), 
            values
        )
        values['updated_at'] = datetime.now(timezone.utc)
            
        return values

class WastageInventoryValidations(BaseValidators):
    """Validators specific to wastage inventory"""
    
    @field_validator('inventory_id', mode='before')
    def validate_inventory_id(cls, v):
        return cls.format_id_field(v, 'INV')

    @field_validator('project_id', mode='before')
    def validate_project_id(cls, v):
        return cls.format_id_field(v, 'PRJ')

    @field_validator('product_id', mode='before')
    def validate_product_id(cls, v):
        return cls.format_id_field(v, 'PRD')

    @field_validator('quantity', mode='before')
    def validate_wastage_quantity(cls, v):
        """Special quantity validator for wastage that requires whole numbers"""
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
    def validate_wastage_dates(cls, v):
        return cls.validate_date_field(v)
    

# from .validations.inventory_validations import (
#     AssignmentInventoryValidations,
#     EntryInventoryValidations,
#     ToEventInventoryValidations,
#     WastageInventoryValidations,
#     AssignmentStatusEnum,
#     EventStatusEnum
# )