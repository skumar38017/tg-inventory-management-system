#  backend/app/models/assign_inventory_model.py

from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Enum, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime, date
from enum import Enum as PyEnum
from backend.app.database.base import Base  # Assuming you have a base class for your models

class AssignmentInventory(Base):
    __tablename__ = "assignment_inventory"
    __table_args__ = (
        # Composite index for employee_name with frequently queried fields
        Index('idx_employee_name_status', 'employee_name', 'status'),
        Index('idx_employee_name_inventory', 'employee_name', 'inventory_id'),
        Index('idx_employee_name_project', 'employee_name', 'project_id'),
        # Single column index for employee_name
        Index('idx_employee_name', 'employee_name'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True)
    assign_to = Column(String, index=True, nullable=True)
    employee_name = Column(String, nullable=False, index=True)  # Made non-nullable since you'll query by this
    sno = Column(String, nullable=True)
    zone_activity = Column(String, nullable=True)
    inventory_id = Column(String, index=True, nullable=True)
    project_id = Column(String, index=True, nullable=True)
    product_id = Column(String, index=True, nullable=True)
    inventory_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(String, nullable=True)
    status = Column(String, nullable=True)
    purpose_reason = Column(String, nullable=True)
    assigned_date = Column(Date, nullable=True)
    submission_date = Column(DateTime, nullable=True)
    assign_by = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    assignment_return_date = Column(Date, nullable=True)
    assignment_barcode = Column(String, nullable=True)
    assignment_barcode_unique_code = Column(String, nullable=True)
    assignment_barcode_image_url = Column(String, nullable=True)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)

    def __repr__(self):
        return f"<AssignmentInventory(employee='{self.employee_name}', inventory='{self.inventory_name}', status='{self.status}')>"