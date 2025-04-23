#  backend/app/models/to_event_inventry_model.py

import uuid
from sqlalchemy import Column, String, Date, DateTime, Index, Integer, ForeignKey
from sqlalchemy.sql import func
from backend.app.database.base import Base
from datetime import datetime, timezone
from barcode import Code128
from barcode.writer import ImageWriter
from sqlalchemy.orm import relationship
import os
import hashlib
from typing import Dict, Any
import logging
from sqlalchemy.dialects.postgresql import UUID

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ToEventInventory(Base):
    __tablename__ = "to_event_inventory"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    
    # Project information fields
    project_id = Column(String, unique=True, nullable=True)
    employee_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    client_name = Column(String, nullable=True)
    setup_date = Column(Date, nullable=True)
    project_name = Column(String, nullable=True)
    event_date = Column(Date, nullable=True)
    submitted_by = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)
    
    # Barcode   
    project_barcode = Column(String, nullable=True)
    project_barcode_unique_code = Column(String, nullable=True)
    project_barcode_image_url = Column(String, nullable=True)
    
    # Relationship to inventory items
    items = relationship("InventoryItem", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_to_event_inventory_created_at', 'created_at'),
            Index('ix_to_event_inventory_updated_at', 'updated_at'),
        Index('ix_to_event_inventory_project_id', 'project_id'),
    )

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    
    # Foreign key to project
    project_id = Column(UUID(as_uuid=True), ForeignKey('to_event_inventory.id'), nullable=False)
    
    # Inventory item fields
    zone_active = Column(String, nullable=True)
    sno = Column(String, nullable=True)
    name = Column(String, nullable=True)  # Changed to match migration
    description = Column(String, nullable=True)
    quantity = Column(String, nullable=True)
    RecQty = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    total = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    per_unit_power = Column(String, nullable=True)
    total_power = Column(String, nullable=True)
    status = Column(String, nullable=True)
    poc = Column(String, nullable=True)
    
    # Relationship back to project
    project = relationship("ToEventInventory", back_populates="items")

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super().__init__(**kwargs)

    def __repr__(self):
        return (
            f"<InventoryItem(id={self.id}, name={self.name})>"  # Changed to use self.name instead of self.inventory_name
            f"\n\tProject ID: {self.project_id}"
            f"\n\tZone Active: {self.zone_active}"
            f"\n\tSNO: {self.sno}"
            f"\n\tName: {self.name}"
            f"\n\tDescription: {self.description}"
            f"\n\tQuantity: {self.quantity}"
            f"\n\tRecQty: {self.RecQty}"
            f"\n\tComments: {self.comments}"
            f"\n\tTotal: {self.total}"
            f"\n\tUnit: {self.unit}"
            f"\n\tPer Unit Power: {self.per_unit_power}"
            f"\n\tTotal Power: {self.total_power}"
            f"\n\tStatus: {self.status}"   
            f"\n\tPOC: {self.poc}"
        )