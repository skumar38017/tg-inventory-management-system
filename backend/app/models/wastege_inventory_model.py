#  backend/app/models/assign_inventory_model.py
from app.models.common_imports import *

class WastageInventory(Base):
    __tablename__ = "wastage_inventories"
    
    id = Column(String, primary_key=True, index=True)
    assign_to = Column(String, nullable=True)
    sno = Column(String, nullable=True)
    employee_name = Column(String, nullable=True)
    inventory_id = Column(String, nullable=True)
    project_id = Column(String, nullable=True)
    product_id = Column(String, nullable=True)
    inventory_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(String, nullable=True)
    status = Column(String, nullable=True)
    receive_date = Column(Date, nullable=True)
    event_date = Column(Date, nullable=True)
    receive_by = Column(String, nullable=True)
    check_status = Column(String, nullable=True)
    location = Column(String, nullable=True)
    project_name = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    zone_activity = Column(String, nullable=True)
    
    # Barcode fields
    wastage_barcode = Column(String, nullable=True)
    wastage_barcode_unique_code = Column(String, nullable=True)
    wastage_barcode_image_url = Column(String, nullable=True)
    
    # Wastage specific fields
    wastage_reason = Column(String, nullable=True)
    wastage_date = Column(Date, nullable=True)
    wastage_approved_by = Column(String, nullable=True)
    wastage_status = Column(String, nullable=True)
    
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)

    def __repr__(self):
        return f"<AssignmentInventory(employee='{self.employee_name}', inventory='{self.inventory_name}', status='{self.status}')>"