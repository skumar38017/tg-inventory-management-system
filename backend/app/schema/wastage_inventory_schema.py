#  backend/app/schema/wastage_inventory_schema

from app.utils.common_imports import *

from app.schema.entry_inventory_schema import StoreInventoryRedis, InventoryRedisOut
from app.schema.to_event_inventry_schma import ToEventRedisOut, ToEventInventoryOut, ToEventRedisUpdateOut, InventoryItemOut
from app.schema.assign_inventory_schema import AssignmentInventoryRedisOut
from app.models.wastege_inventory_model import WastageInventory

class WastageInventoryBase(BaseModel):
    assign_to: Optional[str] = None
    sno: Optional[str] = None
    employee_name: Optional[str] = None
    inventory_id: Optional[Union[str, float, int]] = None
    project_id: Optional[Union[str, float, int]] = None
    product_id: Optional[Union[str, float, int]] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None
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
    sno: Optional[Union[str, int, str]] = None
    employee_name: Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None
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
    sno: Optional[Union[str, float, int]] = None
    employee_name: Optional[str] = None
    inventory_id: Optional[str] = None
    project_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None
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



class WastageInventoryUpdate(BaseModel):
    assign_to: Optional[str] = None
    sno: Optional[Union[str, float, int]] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None
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
        StoreInventoryRedis,
        Dict[str, Any]
    ]
    
    model_config = ConfigDict(
        extra="allow"
    )

