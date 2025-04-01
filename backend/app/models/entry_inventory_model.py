# backend/app/models/entry_inventory_model.py

import uuid
import random
from sqlalchemy import Column, String, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from backend.app.config import Base

# Helper function to generate random product_id
def generate_product_id():
    return f"PRD{random.randint(100000, 999999)}"

# Helper function to generate random inventory_id
def generate_inventory_id():
    return f"INV{random.randint(100000, 999999)}"

class EntryInventory(Base):
    __tablename__ = "entry_inventory"
    
    uuid = Column(String, default=lambda: str(uuid.uuid4()))
    sno = Column(String, index=True, autoincrement=True)
    
    # Automatically generate product_id and inventory_id
    product_id = Column(String, index=True, default=generate_product_id, unique=True)
    inventory_id = Column(String, index=True, default=generate_inventory_id, unique=True, primary_key=True, autoincrement=False)
    
    name = Column(String)
    material = Column(String)
    total_quantity = Column(String)
    manufacturer = Column(String)
    purchase_dealer = Column(String)
    purchase_date = Column(Date)
    purchase_amount = Column(Float)
    repair_quantity = Column(String)
    repair_cost = Column(Float)
    on_rent = Column(String)
    vendor_name = Column(String)
    total_rent = Column(Float)
    rented_inventory_returned = Column(String)
    returned_date = Column(Date)
    on_event = Column(String)
    in_office = Column(String)
    in_warehouse = Column(String)
    issued_qty = Column(String)
    balance_qty = Column(String)
    submitted_by = Column(String)
    created_at = Column(Date, default=func.now())
    updated_at = Column(Date, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return (
            f"<EntryInventory(uuid={self.uuid}, sno={self.sno}, inventory_id={self.inventory_id}, "
            f"product_id={self.product_id}, name={self.name}, material={self.material}, "
            f"total_quantity={self.total_quantity}, manufacturer={self.manufacturer}, "
            f"purchase_dealer={self.purchase_dealer}, purchase_date={self.purchase_date}, "
            f"purchase_amount={self.purchase_amount}, repair_quantity={self.repair_quantity}, "
            f"repair_cost={self.repair_cost}, on_rent={self.on_rent}, vendor_name={self.vendor_name}, "
            f"total_rent={self.total_rent}, rented_inventory_returned={self.rented_inventory_returned}, "
            f"returned_date={self.returned_date}, on_event={self.on_event}, in_office={self.in_office}, "
            f"in_warehouse={self.in_warehouse}, issued_qty={self.issued_qty}, balance_qty={self.balance_qty}, "
            f"submitted_by={self.submitted_by}, created_at={self.created_at}, updated_at={self.updated_at})>"
        )
