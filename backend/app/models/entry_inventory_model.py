# backend/app/models/entry_inventory_model.py

from app.models.common_imports import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class EntryInventory(Base):
    __tablename__ = "entry_inventory"
    
    id = Column(String, primary_key=True)
    sno = Column(String, nullable=True)
    product_id = Column(String, index=True, nullable=False, unique=True)
    inventory_id = Column(String, index=True, nullable=False, unique=True)
    inventory_name = Column(String, nullable=True)
    material = Column(String, nullable=True)
    total_quantity = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    purchase_dealer = Column(String, nullable=True)
    purchase_date = Column(Date, nullable=True)
    purchase_amount = Column(String, nullable=True)
    repair_quantity = Column(String, nullable=True)
    repair_cost = Column(String, nullable=True)
    on_rent = Column(String, nullable=False, default="false")
    vendor_name = Column(String, nullable=True)
    total_rent = Column(String, nullable=True)
    rented_inventory_returned = Column(String, nullable=False, default="false")
    returned_date = Column(Date, nullable=True)
    on_event = Column(String, nullable=False, default="false")
    in_office = Column(String, nullable=False, default="false")
    in_warehouse = Column(String, nullable=False, default="false")
    issued_qty = Column(String, nullable=True)
    balance_qty = Column(String, nullable=True)
    submitted_by = Column(String, nullable=True)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)
    inventory_barcode = Column(String, unique=True, nullable=False)
    inventory_unique_code = Column(String, unique=True, nullable=False)
    inventory_barcode_url = Column(String, nullable=True, default=None)
    inventory_qrcode_url = Column(String, nullable=True, default=None)
    
    __table_args__ = (
        Index('ix_entry_inventory_created_at', 'created_at'),
        Index('ix_entry_inventory_updated_at', 'updated_at'),
        Index('ix_entry_inventory_product_id', 'product_id'),
        Index('ix_entry_inventory_inventory_id', 'inventory_id'),
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)  # Call the parent constructor
