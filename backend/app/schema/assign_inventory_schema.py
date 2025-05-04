#  backend/app/schema/assign_inventory_schema
from backend.app.utils.common_imports import *

from backend.app.schema.entry_inventory_schema import EntryInventoryOut, InventoryRedisOut
from backend.app.schema.to_event_inventry_schma import ToEventRedisOut, ToEventInventoryOut, ToEventRedisUpdateOut, InventoryItemOut



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
    status: Optional[str] = None
    purpose_reason:  Optional[str] = None
    assigned_date: Optional[date] = None
    assign_by:  Optional[str] = None
    assignment_return_date: Optional[date] = None
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
    id: Optional[str] = Field(None, frozen=True) 
    assign_to: Optional[str] = None
    inventory_id: Optional[str] = Field(None, frozen=True) 
    project_id: Optional[str] = Field(None, frozen=True) 
    product_id: Optional[str] = Field(None, frozen=True) 
    employee_name: Optional[str] = Field(None, frozen=True) 
    sno: Optional[str] = None
    zone_activity: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None
    status: Optional[str] = None
    purpose_reason: Optional[str] = None
    assigned_date: Optional[Union[str, date]] = None
    submission_date: Optional[Union[str, datetime]] = None
    assign_by: Optional[str] = None
    comment: Optional[str] = None
    assignment_return_date: Optional[Union[str, date]] = None
    assignment_barcode: Optional[str] = Field(None, frozen=True) 
    assignment_barcode_unique_code: Optional[str] = Field(None, frozen=True) 
    assignment_barcode_image_url: Optional[str] = Field(None, frozen=True) 
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        },
        extra='forbid'
    )

    @field_validator('assigned_date', 'assignment_return_date', mode='before')
    def parse_date_fields(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return value
        return value

    @field_validator('submission_date', 'created_at', 'updated_at', mode='before')
    def parse_datetime_fields(cls, value):
        if isinstance(value, str):
            try:
                # Try ISO format first
                if 'T' in value:
                    return datetime.fromisoformat(value.split('+')[0])
                # Try space-separated format
                elif ' ' in value:
                    return datetime.strptime(value.split('+')[0], '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                return value
        return value
    
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
    status: Optional[str] = None
    purpose_reason: Optional[str] = None
    assigned_date: Optional[date] = None
    submission_date: Optional[Union[str, datetime]] = None
    assign_by: Optional[str] = None
    comment: Optional[str] = None
    assignment_return_date: Optional[date] = None
    assignment_barcode: Optional[str] = None
    assignment_barcode_unique_code: Optional[str] = None
    assignment_barcode_image_url: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None  
    updated_at: Optional[Union[str, datetime]] = None

    @field_validator('submission_date', 'created_at', 'updated_at', mode='before')
    def parse_datetime(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).replace(tzinfo=None)
            except ValueError:
                return None
        elif isinstance(value, datetime):
            return value.replace(tzinfo=None)
        return value
    
    @field_validator('assigned_date', 'assignment_return_date', mode='before')
    def parse_date(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None
        elif isinstance(value, datetime):
            return value.date()
        return value

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
            StatusEnum: lambda v: v.value
        },
        extra='forbid'
    )

    @field_serializer('created_at', 'updated_at', 'submission_date')
    def serialize_dt(self, dt: datetime | None, _info) -> str | None:
        if dt is None:
            return None
        return dt.isoformat()

class AssignmentInventoryRedisOut(AssignmentInventoryOut):
    success: Optional[bool] = Field(None, exclude=True)  # Mark as excluded from schema
    message: Optional[str] = Field(None, exclude=True)  # Mark as excluded from schema

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
            StatusEnum: lambda v: v.value
        },
        extra='ignore'  # Changed from 'forbid' to 'ignore'
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
    status: Optional[str] = None
    purpose_reason: Optional[str] = None
    assign_by: Optional[str] = None
    comment: Optional[str] = None
    submission_date: Optional[Union[str, datetime]] = None
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