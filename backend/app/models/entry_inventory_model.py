# backend/app/models/entry_inventory_model.py
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

class EntryInventory(Base):
    __tablename__ = "entry_inventory"
    
    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sno = Column(String, index=True)
    product_id = Column(String, index=True, nullable=False, unique=True)
    inventory_id = Column(String, index=True, nullable=False, unique=True)
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    bar_code = Column(String, unique=True, nullable=False)
    unique_code = Column(String, unique=True, nullable=False)
    
    __table_args__ = (
        Index('ix_entry_inventory_created_at', 'created_at'),
        Index('ix_entry_inventory_updated_at', 'updated_at'),
        Index('ix_entry_inventory_product_id', 'product_id'),
        Index('ix_entry_inventory_inventory_id', 'inventory_id'),
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)  # Call the parent constructor

    def generate_linked_codes(self) -> tuple[str, str]:
        """Generate cryptographically linked bar_code and unique_code"""
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
            
        composite_data = (
            f"{self.uuid}|{self.product_id}|{self.inventory_id}|"
            f"{self.name[:20]}|{self.created_at.isoformat()}"
        )
        
        hash_digest = hashlib.sha256(composite_data.encode()).hexdigest()
        bar_code = ''.join([d for d in hash_digest if d.isdigit()])[:12].ljust(12, '0')
        
        unique_code = hashlib.blake2b(
            bar_code.encode(),
            key=self.uuid.encode(),
            digest_size=8
        ).hexdigest().upper()
        
        return bar_code, unique_code


    def create_barcode_image(self, bar_code: str, unique_code: str, save_path: str = 'static/barcodes') -> str:
        """Generate barcode image with both codes"""
        os.makedirs(save_path, exist_ok=True)

        # Use a simpler approach with default writer
        from barcode.writer import ImageWriter

        # Customize the writer options
        writer_options = {
            'module_width': 0.4,
            'module_height': 15,
            'font_size': 12,
            'text_distance': 5,
            'quiet_zone': 10,
            'write_text': False  # We'll handle text manually
        }

        # Generate the barcode
        code = Code128(bar_code, writer=ImageWriter())

        # Save to file
        filename = os.path.join(save_path, f"{bar_code}_{unique_code}")
        full_path = code.save(filename, writer_options)

        # Now add the text manually using PIL
        from PIL import Image, ImageDraw, ImageFont
        try:
            img = Image.open(full_path)
            draw = ImageDraw.Draw(img)

            # Use default font or specify a path to a TTF file
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()

            # Calculate text positions
            width, height = img.size
            text_ypos = height - 30

            # Draw both codes
            draw.text(
                (width/2, text_ypos),
                f"ID: {bar_code}",
                font=font,
                fill="black",
                anchor="ms"
            )
            draw.text(
                (width/2, text_ypos + 15),
                f"UID: {unique_code}",
                font=font,
                fill="black",
                anchor="ms"
            )

            # Save the modified image
            img.save(full_path)
            return full_path

        except Exception as e:
            # If text addition fails, at least we have the barcode
            logger.error(f"Error adding text to barcode: {e}")
            return full_path
        
    def verify_code_relationship(self) -> bool:
        """Verify that unique_code correctly signs the bar_code"""
        expected_unique = hashlib.blake2b(
            self.bar_code.encode(),
            key=self.uuid.encode(),
            digest_size=8
        ).hexdigest().upper()
        return self.unique_code == expected_unique
    
    def get_public_details(self) -> Dict[str, Any]:
        """Return safe-to-share information for public scanning"""
        return {
            'company': "Tagglabs Experiential PVT. LTD.",
            'name': self.name,
            'product_id': self.product_id,
            'inventory_id': self.inventory_id,
            'manufacturer': self.manufacturer,
            'purchase_date': str(self.purchase_date) if self.purchase_date else None,
            'status': 'Available' if not bool(self.on_rent) else 'On Rent',
            'contact': 'inventory@tagglabs.com'
        }

    def get_private_details(self, requester: Any) -> Dict[str, Any]:
        """Return full details for authorized users"""
        base_details = self.get_public_details()
        
        if requester.role in ['admin', 'owner']:
            return {
                **base_details,
                'purchase_amount': self.purchase_amount,
                'vendor': self.vendor_name,
                'location': self.in_office if self.in_office else self.in_warehouse,
                'submitted_by': self.submitted_by,
                'maintenance_history': {
                    'repairs': self.repair_quantity,
                    'last_service': str(self.returned_date) if self.returned_date else None
                },
                'system_ids': {
                    'uuid': self.uuid,
                    'unique_code': self.unique_code
                }
            }
        elif requester.role == 'staff':
            return {
                **base_details,
                'location': self.in_office if self.in_office else self.in_warehouse,
                'last_updated': str(self.updated_at)
            }
        return base_details

    @staticmethod
    def validate_product_id(product_id: str) -> str:
        """Validate product ID format (PRD followed by numbers)"""
        if not product_id.startswith('PRD') or not product_id[3:].isdigit():
            raise ValueError("ProductID must be in format PRD followed by numbers")
        return product_id

    @staticmethod
    def validate_inventory_id(inventory_id: str) -> str:
        """Validate inventory ID format (INV followed by numbers)"""
        if not inventory_id.startswith('INV') or not inventory_id[3:].isdigit():
            raise ValueError("InventoryID must be in format INV followed by numbers")
        return inventory_id

    def __repr__(self) -> str:
        return f"<EntryInventory(uuid={self.uuid}, name={self.name}, product_id={self.product_id})>"

# Event listener for automatic code generation
@event.listens_for(EntryInventory, 'before_insert')
def generate_linked_codes(mapper, connection, target):
    # Generate linked codes using instance method
    bar_code, unique_code = target.generate_linked_codes()
    
    # Ensure uniqueness
    while connection.execute(
        select(EntryInventory).where(
            (EntryInventory.bar_code == bar_code) |
            (EntryInventory.unique_code == unique_code)
        )
    ).first():
        target.uuid = str(uuid.uuid4())
        bar_code, unique_code = target.generate_linked_codes()
    
    # Assign codes
    target.bar_code = bar_code
    target.unique_code = unique_code
    
    # Generate barcode image
    target.create_barcode_image(bar_code, unique_code)