#  backend/app/models/to_event_inventry_model.py

import uuid
from sqlalchemy import Column, String, Date, DateTime, Index
from sqlalchemy.sql import func
from backend.app.database.base import Base
from datetime import datetime, timezone
from barcode import Code128
from barcode.writer import ImageWriter
from sqlalchemy import event, select
import os
import hashlib
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ToEventInventory(Base):
    __tablename__ = "to_event_inventory"  # Fixed typo in table name (was "inventry")
    
    uuid = Column(String, primary_key=True)  # Added default UUID generation
    sno = Column(String, nullable=True)
    name = Column(String, nullable=True)
    zone_active = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(String, nullable=True)  
    material = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    total = Column(String, nullable=True)  
    unit = Column(String, nullable=True)
    project_id = Column(String, unique=True, nullable=True)
    per_unit_power = Column(String, nullable=True)  
    total_power = Column(String, nullable=True)
    status = Column(String, nullable=True)
    poc = Column(String, nullable=True)
    employee_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    client_name = Column(String, nullable=True)
    setup_date = Column(Date, nullable=True) 
    project_name = Column(String, nullable=True)
    event_date = Column(Date, nullable=True)  
    submitted_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    project_barcode = Column(String, unique=True, nullable=True)
    project_barcode_unique_code = Column(String, unique=True, nullable=True)
    project_barcode_image_url = Column(String, nullable=True, unique=True, default=None)
    
    __table_args__ = (
        Index('ix_to_event_inventory_created_at', 'created_at'),
        Index('ix_to_event_inventory_updated_at', 'updated_at'),
        Index('ix_to_event_inventory_project_id', 'project_id'),
    )

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super().__init__(**kwargs)