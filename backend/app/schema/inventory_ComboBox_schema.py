# backend/app/schema/inventory_ComboBox_schema.py
from pydantic import BaseModel, field_validator, ConfigDict, Field
from datetime import datetime, date, timezone
from typing import Optional, Union, Dict, Any, List
import uuid
import json
import re
from typing import Union
from enum import Enum
from pydantic import ValidationError
from backend.app.schema.entry_inventory_schema import EntryInventoryOut, InventoryRedisOut
from backend.app.schema.to_event_inventry_schma import ToEventRedisOut, ToEventInventoryOut, ToEventRedisUpdateOut, InventoryItemOut
from backend.app.schema.assign_inventory_schema import AssignmentInventoryRedisOut
from backend.app.models.wastege_inventory_model import WastageInventory
from backend.app.utils.field_validators import (
    BaseValidators,
)

class InventoryComboBoxItem(BaseModel):
    # Common fields
    key_type: Optional[str] = None
    uuid: Optional[str] = None
    id: Optional[Union[str, int]] = None
    sno: Optional[Union[str, int]] = None
    inventory_id: Optional[str] = None
    product_id: Optional[str] = None
    project_id: Optional[str] = None
    name: Optional[str] = None
    inventory_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Union[str, int]] = None
    status: Optional[str] = None
    location: Optional[str] = None
    project_name: Optional[str] = None
    event_date: Optional[Union[str, int, date]] = None
    comment: Optional[str] = None
    comments: Optional[str] = None
    zone_activity: Optional[str] = None
    zone_active: Optional[str] = None
    submitted_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Assignment specific fields
    assign_to: Optional[str] = None
    employee_name: Optional[str] = None
    purpose_reason: Optional[str] = None
    assigned_date: Optional[Union[str, int, date]] = None
    assign_by: Optional[str] = None
    assignment_return_date: Optional[Union[str, int, date]] = None
    assignment_barcode: Optional[Union[str, int]] = None
    assignment_barcode_image_url: Optional[str] = None
    submission_date: Optional[Union[str, int, date]] = None
    
    # Receiving/Wastage specific fields
    receive_date: Optional[Union[str, int, date]] = None
    receive_by: Optional[str] = None
    check_status: Optional[str] = None
    wastage_reason: Optional[str] = None
    wastage_date: Optional[Union[str, int, date]] = None
    wastage_approved_by: Optional[str] = None
    wastage_status: Optional[str] = None
    wastage_barcode: Optional[Union[str, int]] = None
    wastage_barcode_image_url: Optional[str] = None
    
    # Event/Project specific fields
    client_name: Optional[str] = None
    setup_date: Optional[Union[str, int, date]] = None
    material: Optional[str] = None
    total: Optional[Union[str, int, float]] = None
    unit: Optional[Union[str, int]] = None
    per_unit_power: Optional[Union[str, int]] = None
    total_power: Optional[Union[str, int]] = None
    poc: Optional[str] = None
    
    # Inventory item specific fields
    total_quantity: Optional[Union[str, int]] = None
    manufacturer: Optional[str] = None
    purchase_dealer: Optional[str] = None
    purchase_date: Optional[Union[str, int, date]] = None
    purchase_amount: Optional[Union[str, int, float]] = None
    repair_quantity: Optional[Union[str, int]] = None
    repair_cost: Optional[Union[str, int, float]] = None
    on_rent: Optional[Union[str, bool]] = None
    vendor_name: Optional[str] = None
    total_rent: Optional[Union[str, int, float]] = None
    rented_inventory_returned: Optional[Union[str, bool]] = None
    on_event: Optional[Union[str, bool]] = None
    in_office: Optional[Union[str, bool]] = None
    in_warehouse: Optional[Union[str, bool]] = None
    issued_qty: Optional[Union[str, int]] = None
    balance_qty: Optional[Union[str, int]] = None
    bar_code: Optional[Union[str, int]] = None
    barcode_image_url: Optional[str] = None

    @field_validator(
        'on_rent', 'rented_inventory_returned', 'on_event', 
        'in_office', 'in_warehouse', mode='before'
    )
    def convert_bool_to_string(cls, v):
        if isinstance(v, bool):
            return str(v).lower()
        return v

class InventoryComboBoxResponse(BaseModel):
    items: List[InventoryComboBoxItem]
    total_count: int
