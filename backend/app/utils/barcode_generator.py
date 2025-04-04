#  backend/app/utils/barcode_generator.py

import uuid
import hashlib
from datetime import datetime, timezone
from typing import Tuple
import os
from barcode import Code128
from barcode.writer import ImageWriter
from fastapi import HTTPException
import logging
import json
import base64
from PIL import Image
from io import BytesIO
from typing import Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BarcodeGenerator:
    @staticmethod
    def generate_linked_codes(entry_data: dict) -> Tuple[str, str, str]:
        """
        Generate cryptographically linked barcode, unique code, and image URL
        
        Args:
            entry_data: Dictionary containing inventory entry data
            
        Returns:
            Tuple of (barcode, unique_code, image_url)
        """
        try:
            # Ensure required fields exist
            if not entry_data.get('uuid'):
                entry_data['uuid'] = str(uuid.uuid4())
            if not entry_data.get('created_at'):
                entry_data['created_at'] = datetime.now(timezone.utc)
            
            # Create composite data for hashing
            composite_data = (
                f"{entry_data['uuid']}|{entry_data.get('project_id', '')}|"
                f"{entry_data.get('name', '')[:20]}|{entry_data['created_at'].isoformat()}"
            )
            
            # Generate barcode
            hash_digest = hashlib.sha256(composite_data.encode()).hexdigest()
            barcode = ''.join([d for d in hash_digest if d.isdigit()])[:12].ljust(12, '0')
            
            # Generate unique verification code
            unique_code = hashlib.blake2b(
                barcode.encode(),
                key=entry_data['uuid'].encode(),
                digest_size=8
            ).hexdigest().upper()
            
            # Generate barcode image
            image_url = BarcodeGenerator.generate_barcode_image(barcode)
            
            return barcode, unique_code, image_url
            
        except Exception as e:
            logger.error(f"Barcode generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate barcode: {str(e)}"
            )

    @staticmethod
    def generate_barcode_image(barcode: str, base_dir: str = "static/barcodes") -> str:
        """
        Generate and save barcode image, return URL
        
        Args:
            barcode: The barcode string to generate image for
            base_dir: Directory to save images (relative to project root)
            
        Returns:
            URL path to the generated image
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(base_dir, exist_ok=True)
            
            # Generate barcode image
            code = Code128(barcode, writer=ImageWriter())
            filename = f"{barcode}_{int(datetime.now(timezone.utc).timestamp())}"
            filepath = os.path.join(base_dir, filename)
            
            # Save image
            code.save(filepath, options={
                'write_text': False,
                'module_width': 0.4,
                'module_height': 15.0,
                'quiet_zone': 6.5
            })
            
            # Return relative URL path
            return f"/{base_dir}/{filename}.png"
            
        except Exception as e:
            logger.error(f"Barcode image generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate barcode image: {str(e)}"
            )

    @staticmethod
    def verify_code_relationship(barcode: str, unique_code: str, entry_uuid: str) -> bool:
        """
        Verify that unique_code correctly signs the barcode
        
        Args:
            barcode: The barcode to verify
            unique_code: The verification code
            entry_uuid: UUID of the inventory entry
            
        Returns:
            bool: True if verification succeeds
        """
        expected_unique = hashlib.blake2b(
            barcode.encode(),
            key=entry_uuid.encode(),
            digest_size=8
        ).hexdigest().upper()
        
        return unique_code == expected_unique
        
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