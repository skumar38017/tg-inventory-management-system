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