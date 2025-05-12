#  backend/app/schema/qrcode_barcode_schema.py
from backend.app.utils.common_imports import *

class InventoryQrCodeResponse(BaseValidators, BaseModel):
    company: Optional[str] = "Tagglabs Experiential PVT. LTD."
    type: Optional[str] = "inventory"
    # Include all possible fields from Redis
    id: Optional[Union[str, int]] = None
    product_id: Optional[str] = None
    inventory_id: Optional[str] = None
    sno: Optional[Union[str, int]] = None
    inventory_name: Optional[str] = None
    material: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[Union[str, date]] = None
    on_rent: Optional[Union[str, bool]] = False
    on_event: Optional[Union[str, bool]] = False
    in_office: Optional[Union[str, bool]] = False
    in_warehouse: Optional[Union[str, bool]] = False
    submitted_by: Optional[str] = None
    updated_at: Optional[Union[str, datetime]] = None
    created_at: Optional[Union[str, datetime]] = None
            
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )


class BarcodeClallanScanResponse(BaseModel):
    id: Optional[Union[str, int]] = None
    sno: Optional[Union[str, int]] = None
    inventory_id: Optional[str] = None
    product_id: Optional[str] = None
    inventory_name: Optional[str] = None
    material: Optional[Union[str, int]] = None
    total_quantity: Optional[Union[str, float, int]] = 1
    manufacturer: Optional[str] = "tagglabs"
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[Union[str, date]] = Field(default_factory=lambda: date.today().isoformat())
    purchase_amount: Optional[Union[str, float, int]] = None
    repair_quantity: Optional[Union[str, float, int]] = None
    on_rent: Optional[str] = "false"
    vendor_name: Optional[str] = "unknown"
    total_rent: Optional[Union[str, float, int]] = 0
    rented_inventory_returned: Optional[str] = "false"
    returned_date: Optional[Union[str, date]] = Field(default_factory=lambda: date.today().isoformat())
    on_event: Optional[str] = "false"
    in_office: Optional[str] = "false"
    in_warehouse: Optional[str] = "false"
    issued_qty: Optional[Union[str, float, int]] = 1
    balance_qty: Optional[Union[str, float, int]] = None
    submitted_by: Optional[str] = "Inventory_admin"
    created_at: Optional[Union[str, datetime]] = Field(default_factory=lambda: datetime.now().strftime("%m/%d/%Y %I:%M %p"))
    updated_at: Optional[Union[str, datetime]] = Field(default_factory=lambda: datetime.now().strftime("%m/%d/%Y %I:%M %p"))
    inventory_qrcode_url: Optional[str] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),
            date: lambda v: UTCDateUtils.format_date(v)
        }
    )

class BarcodeClallanScan(BaseValidators, BaseModel):
    barcode_value: Optional[str] = Field(None, description="Barcode value")
    unique_code: Optional[str] = Field(None, description="Unique code")

class BarcodeScan(BaseValidators, BaseModel):
    id: Optional[str] = None

    # Common fields
    sno: Optional[Union[str, int]] = None
    inventory_id: Optional[Union[str, int]] = None
    product_id: Optional[Union[str, int]] = None
    project_id: Optional[Union[str, int]] = None
    name: Optional[Union[str, int]] = None
    inventory_name: Optional[Union[str, int]] = None
    description: Optional[Union[str, int]] = None
    quantity: Optional[Union[str, int]] = 1
    status: Optional[Union[str, int]] = None
    location: Optional[str] = None
    project_name: Optional[str] = None
    event_date: Optional[Union[str, int, date]] = Field(default_factory=lambda: date.today().isoformat())
    comment: Optional[str] = None
    comments: Optional[str] = None
    zone_activity: Optional[Union[str, int]] = None
    zone_active: Optional[Union[str, int]] = None
    submitted_by: Optional[str] = "Inventory Admin"
    
    # Assignment specific fields
    assign_to: Optional[str] = "Employee"
    employee_name: Optional[str] = "Unknown"
    purpose_reason: Optional[str] = None
    assigned_date: Optional[Union[str, int, date]] = Field(default_factory=lambda: date.today().isoformat())
    assign_by: Optional[str] = "Inventory_Admin"
    submission_date: Optional[Union[str, int, date]] = Field(default_factory=lambda: date.today().isoformat())
    
    # Receiving/Wastage specific fields
    receive_date: Optional[Union[str, int, date]] = Field(default_factory=lambda: date.today().isoformat())
    receive_by: Optional[str] = "Inventory Admin"
    check_status: Optional[str] = "Ok"
    wastage_reason: Optional[str] = "Not Working"
    wastage_date: Optional[Union[str, int, date]] = Field(default_factory=lambda: date.today().isoformat())
    wastage_approved_by: Optional[str] = "Inventory Admin"
    wastage_status: Optional[Union[str, int]] = "Approved"
    
    # Event/Project specific fields
    material: Optional[str] = None
    total: Optional[Union[str, int, float]] = 1
    unit: Optional[Union[str, int]] = "PCS"
    per_unit_power: Optional[Union[str, int]] = 1
    total_power: Optional[Union[str, int]] = 1
    poc: Optional[Union[str, int]] = "Admin"
    
    # Inventory item specific fields
    total_quantity: Optional[Union[str, int]] = 1
    manufacturer: Optional[str] = "Tahgglabs"
    purchase_dealer: Optional[str] = "Unknown"
    purchase_date: Optional[Union[str, int, date]] = Field(default_factory=lambda: date.today().isoformat())
    purchase_amount: Optional[Union[str, int, float]] = 0
    repair_quantity: Optional[Union[str, int]] = 0
    repair_cost: Optional[Union[str, int, float]] = 0
    on_rent: Optional[Union[str, bool]] = "false"
    vendor_name: Optional[str] = "unknown"
    total_rent: Optional[Union[str, int, float]] = 0
    rented_inventory_returned: Optional[Union[str, bool]] = "false"
    on_event: Optional[Union[str, bool]] = "false"
    in_office: Optional[Union[str, bool]] = "true"
    in_warehouse: Optional[Union[str, bool]] = "false"
    issued_qty: Optional[Union[str, int]] = 1
    balance_qty: Optional[Union[str, int]] = None
    returned_date: Optional[Union[str, date]] = None
    inventory_qrcode_url: Optional[str] = None
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None

    @field_validator(
        'on_rent', 'rented_inventory_returned', 'on_event', 
        'in_office', 'in_warehouse', mode='before'
    )
    def convert_bool_to_string(cls, v):
        if isinstance(v, bool):
            return str(v).lower()
        return v

    class Config:
        extra = "allow"

class BarcodeScanResponse(BaseModel):
    items: List[BarcodeScan]
    total_count: int

    class Config:
        extra = "allow"