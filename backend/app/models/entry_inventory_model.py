# backend/app/models/entry_inventory_model.py
import uuid
from sqlalchemy import Column, String, Date, DateTime, Index
from sqlalchemy.sql import func
from app.database.base import Base
from datetime import datetime, timezone

class EntryInventory(Base):
    __tablename__ = "entry_inventory"
    
    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sno = Column(String, index=True)
    
    # ID fields - prefixes will be added automatically
    product_id = Column(String, index=True, nullable=False, unique=True)
    inventory_id = Column(String, index=True, nullable=False, unique=True)
    
    # Other fields
    name = Column(String)
    material = Column(String)
    total_quantity = Column(String)
    manufacturer = Column(String)
    purchase_dealer = Column(String)
    purchase_date = Column(Date)
    purchase_amount = Column(String)
    repair_quantity = Column(String)
    repair_cost = Column(String)
    on_rent = Column(String)
    vendor_name = Column(String)
    total_rent = Column(String)
    rented_inventory_returned = Column(String)
    returned_date = Column(Date)
    on_event = Column(String)
    in_office = Column(String)
    in_warehouse = Column(String)
    issued_qty = Column(String)
    balance_qty = Column(String)
    submitted_by = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('ix_entry_inventory_created_at', 'created_at'),
        Index('ix_entry_inventory_updated_at', 'updated_at'),
        Index('ix_entry_inventory_product_id', 'product_id'),
        Index('ix_entry_inventory_inventory_id', 'inventory_id'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def validate_product_id(product_id: str) -> str:
        if not product_id.startswith('PRD') or not product_id[3:].isdigit():
            raise ValueError("ProductID must be in format PRD followed by numbers")
        return product_id

    @staticmethod
    def validate_inventory_id(inventory_id: str) -> str:
        if not inventory_id.startswith('INV') or not inventory_id[3:].isdigit():
            raise ValueError("InventoryID must be in format INV followed by numbers")
        return inventory_id

    def __repr__(self):
        return f"<EntryInventory(uuid={self.uuid}, product_id={self.product_id}, inventory_id={self.inventory_id})>"