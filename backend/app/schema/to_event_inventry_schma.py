# backend/app/schema/to_event_inventry_schma.py
from app.utils.common_imports import *

class InventoryItemBase(BaseModel):
    zone_active: Optional[str] = Field(None, description="The active zone for this equipment")
    sno: Optional[str] = Field(None, description="Serial number of the equipment")
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None 
    RecQty: Optional[Union[str, float, int]] = None 
    comments: Optional[str] = None
    total: Optional[Union[str, float, int]] = None
    unit: Optional[Union[str, float, int]] = None
    per_unit_power: Optional[Union[str, float, int]] = None 
    total_power: Optional[Union[str, float, int]] = None  
    status: Optional[str] = None
    poc: Optional[str] = None



    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemOut(BaseModel):
    id: Optional[str] = Field(None, frozen=True)
    project_id: Optional[str] = Field(None, frozen=True)
    zone_active: Optional[str] = None
    sno: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None 
    RecQty: Optional[Union[str, float, int]] = None 
    comments: Optional[str] = None
    total: Optional[Union[str, float, int]] = None
    unit: Optional[Union[str, float, int]] = None 
    per_unit_power: Optional[Union[str, float, int]] = None 
    total_power: Optional[Union[str, float, int]] = None 
    status: Optional[str] = None
    poc: Optional[str] = None


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
    setup_date: Optional[Union[str, date]] = None
    project_name: Optional[str] = None
    event_date: Optional[Union[str, date]] = None
    submitted_by: Optional[str] = None
    inventory_items: List[InventoryItemBase]


        
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
    setup_date: Optional[Union[str, date]] = None
    project_name: Optional[str] = None
    event_date: Optional[Union[str, date]] = None
    submitted_by: Optional[str] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None
    updated_at: datetime = datetime.now(timezone.utc)


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
    event_date: Optional[Union[str, date]] = None  
    submitted_by: Optional[str] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None
    inventory_items: List[InventoryItemOut] = []

    model_config = ConfigDict(from_attributes=True)



    
class ToEventInventoryUpdateOut(ToEventInventoryOut):
    updated_at: datetime


    
    model_config = ConfigDict(from_attributes=True)
    
class ToEventInventorySearch(BaseModel):
    project_id: str
    


class ToEventRedis(BaseModel):
    """Schema for storing inventory in Redis"""
    id: Optional[str] = None
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[Union[str, date]] = None  
    project_name: Optional[str] = None
    event_date: Optional[Union[str, date]] = None  
    submitted_by: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None  
    updated_at: Optional[Union[str, datetime]] = None  
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None
    inventory_items: List[Dict[str, Any]] = []



    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )

# Update Input Schema (fields that can be updated)
class ToEventRedisUpdateIn(BaseModel):
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[Union[str, date]] = None  
    project_name: Optional[str] = None
    event_date: Optional[Union[str, date]] = None  
    submitted_by: Optional[str] = None
    inventory_items: Optional[List[InventoryItemBase]] = None



    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )
 
# Update Output Schema (fields that should be returned)
class ToEventRedisUpdateOut(BaseModel):
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[Union[str, date]] = None  
    project_name: Optional[str] = None
    event_date: Optional[Union[str, date]] = None  
    submitted_by: Optional[str] = None
    inventory_items: List[Dict[str, Any]] = Field(default_factory=list)
    id: Optional[str] = None
    uuid: Optional[str] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None  
    updated_at: Optional[Union[str, datetime]] = None  


        

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )
    
class ToEventRedisOut(ToEventInventoryOut):
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    cretaed_at: Optional[datetime] = None  # Handle the typo field


# ......................................................................................................
class RedisInventoryItem(BaseModel):
    zone_active: Optional[str] = None
    sno: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, float, int]] = None 
    RecQty: Optional[Union[str, float, int]] = None
    comments: Optional[str] = None
    total: Optional[Union[str, float, int]] = None
    unit: Optional[Union[str, float, int]] = None 
    per_unit_power: Optional[Union[str, float, int]] = None
    total_power: Optional[Union[str, float, int]] = None 
    status: Optional[str] = None
    poc: Optional[str] = None
    id: Optional[str] = None
    project_id: Optional[str] = None



class ToEventUploadSchema(BaseModel):
    id: Optional[str] = None
    project_id: Optional[str] = None
    employee_name: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    setup_date: Optional[Union[str, date]] = None
    project_name: Optional[str] = None
    event_date: Optional[Union[str, date]] = None
    submitted_by: Optional[str] = None
    inventory_items: List[RedisInventoryItem]=[]
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    project_barcode: Optional[str] = None
    project_barcode_unique_code: Optional[str] = None
    project_barcode_image_url: Optional[str] = None



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
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None   



    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        },
        extra='ignore'  # Ignore extra fields in response
    )
