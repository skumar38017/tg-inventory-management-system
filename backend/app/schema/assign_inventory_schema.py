#  backend/app/schema/assign_inventory_schema
# backend/app/schema/assign_inventory_schema
from app.schema.common_schema import *


class AssignmentInventoryBase(BaseModel):
    assign_to: Optional[str] = None
    employee_name: Optional[str] = None
    sno: Optional[str] = None
    zone_activity: Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[float, int, str]] = Field(None, ge=0)
    status: Optional[str] = None
    purpose_reason: Optional[str] = None
    assigned_date: Optional[date] = None
    assign_by: Optional[str] = None
    assignment_return_date: Optional[date] = None
    comment: Optional[str] = None

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
    success: Optional[bool] = Field(None, exclude=True)
    message: Optional[str] = Field(None, exclude=True)

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
            StatusEnum: lambda v: v.value
        },
        extra='ignore'
    )

class AssignmentInventorySearch(BaseModel):
    employee_name: Optional[str] = None
    inventory_id: Optional[str] = None

class AssignmentInventoryUpdate(BaseModel):
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
    assigned_date: Optional[date] = Field(None, frozen=True) 
    assignment_return_date: Optional[date] = None
       
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
        },
        extra='forbid'
    )

class AssignmentInventoryUpdateOut(AssignmentInventoryRedisOut):
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