# backend/app/utils/barcode_generator.py

import uuid
import hashlib
import os
from datetime import datetime, timezone
from typing import Tuple, Dict, Any, Optional
import io
import logging
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from backend.app import config
from backend.app.schema.entry_inventory_schema import EntryInventoryCreate, EntryInventoryBarcodeOut

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TransparentImageWriter(ImageWriter):
    """Custom writer for transparent barcode images with text behind bars"""
    def __init__(self):
        super().__init__()
        self._background = 'transparent'
        self._format = 'PNG'
        self.dpi = 300  # Higher DPI for better print quality
        self.text_distance = 2  # Distance between barcode and text
        self.font_size = 10  # Font size for the text

    def calculate_size(self, modules, line_width):
        """Calculate image size with extra space for text"""
        width, height = super().calculate_size(modules, line_width)
        return width, height + 20  # Add space for text below barcode

    def _paint_text(self, xpos, ypos):
        """Override text painting to put it behind the bars"""
        # Don't paint text here - we'll handle it in our custom method
        pass

class BarcodeGenerator:
    def __init__(self):
        # Define the base path for barcode images
        self.barcode_base_path = config.BARCODE_BASE_PATH
        self.barcode_base_url = config.BARCODE_BASE_URL
        
        # Ensure the directory exists
        os.makedirs(self.barcode_base_path, exist_ok=True)

    def generate_linked_codes(self, instance_data: Dict[str, Any], inventory_type: str = None) -> Tuple[str, str]:
        """
        Generate cryptographically linked codes for any inventory type
        Returns: (barcode, unique_code)
        """
        # Ensure we have a UUID (different field names in different models)
        uuid_field = next(
            (f for f in ['uuid', 'id'] if f in instance_data and instance_data[f]),
            None
        )
        if not uuid_field:
            instance_data['uuid'] = str(uuid.uuid4())
        else:
            instance_data['uuid'] = instance_data[uuid_field]

        # Get the appropriate ID fields based on inventory type
        inventory_type = inventory_type or self.detect_inventory_type(instance_data)
        
        # Create composite data based on inventory type
        if inventory_type == 'assignment':
            composite_data = (
                f"{instance_data['uuid']}|{instance_data.get('inventory_id', '')}|"
                f"{instance_data.get('employee_name', '')}|{instance_data.get('assigned_date', '')}"
            )
        elif inventory_type == 'event_inventory':
            composite_data = (
                f"{instance_data['uuid']}|{instance_data.get('project_id', '')}|"
                f"{instance_data.get('client_name', '')}|{instance_data.get('event_date', '')}"
            )
        elif inventory_type == 'wastage':
            composite_data = (
                f"{instance_data['uuid']}|{instance_data.get('inventory_id', '')}|"
                f"{instance_data.get('wastage_date', '')}|{instance_data.get('wastage_reason', '')}"
            )
        elif inventory_type == 'inventory':
            composite_data = (
                f"{instance_data['uuid']}|{instance_data.get('inventory_id', '')}|"
                f"{instance_data.get('inventory_name', '')}|{instance_data.get('created_at', '')}"
            )
        else:
            raise ValueError(f"Invalid inventory_type: {inventory_type}")
        

        # Generate deterministic barcode from hash
        hash_digest = hashlib.sha256(composite_data.encode()).hexdigest()
        barcode = ''.join([d for d in hash_digest if d.isdigit()])[:12].ljust(12, '0')

        # Generate unique code that cryptographically signs the barcode
        unique_code = hashlib.blake2b(
            barcode.encode(),
            key=instance_data['uuid'].encode(),  # UUID is the cryptographic anchor
            digest_size=8
        ).hexdigest().upper()

        return barcode, unique_code

    def detect_inventory_type(self, data: Dict[str, Any]) -> str:
        """Determine inventory type based on field presence"""
        if 'assignment_barcode' in data:
            return 'assignment'
        if 'wastage_barcode' in data:
            return 'wastage'
        if 'project_barcode' in data:
            return 'event_inventory'
        if 'inventory_barcode' in data:
            return 'inventory'
        return 'generic'

    def generate_barcode_image(
        self, 
        barcode_str: str, 
        unique_code: str, 
        save_to_disk: bool = True,
        output_path: Optional[str] = None
    ) -> Tuple[bytes, str]:
        """
        Generate a transparent PNG barcode image with codes printed behind the bars
        Args:
            barcode_str: The barcode number
            unique_code: The unique verification code
            save_to_disk: Whether to save the image to disk
            output_path: Custom path to save the image (defaults to configured path)
        Returns:
            Tuple of (image_bytes, image_url)
        """
        # Create EAN13 barcode (12 digits + checksum)
        ean = barcode.get('ean13', barcode_str, writer=TransparentImageWriter())
        
        # Generate the barcode image with transparent background
        barcode_img = ean.render()
        
        # Convert to RGBA if not already
        if barcode_img.mode != 'RGBA':
            barcode_img = barcode_img.convert('RGBA')
        
        # Create a drawing context
        draw = ImageDraw.Draw(barcode_img)
        
        try:
            # Try to load a nice font
            font = ImageFont.truetype("arial.ttf", 10)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Calculate positions for the text
        text = f"{barcode_str}\n{unique_code}"
        text_width = max(
            draw.textlength(line, font=font) 
            for line in text.split('\n')
        )
        img_width = barcode_img.width
        
        # Calculate vertical position - behind the bars
        text_y_position = barcode_img.height - 25
        
        # Draw semi-transparent background for text (optional)
        # This helps with readability while keeping the background mostly transparent
        text_height = 20
        text_bg = Image.new('RGBA', (barcode_img.width, text_height), (255, 255, 255, 100))
        barcode_img.paste(text_bg, (0, text_y_position - 5), text_bg)
        
        # Draw the text
        for i, line in enumerate(text.split('\n')):
            line_width = draw.textlength(line, font=font)
            draw.text(
                ((img_width - line_width) / 2, text_y_position + (i * 12)),
                line,
                font=font,
                fill="black"  # Dark color for text
            )
        
        # Compress and save to bytes
        img_byte_arr = io.BytesIO()
        barcode_img.save(img_byte_arr, format='PNG', optimize=True, compress_level=9)
        image_bytes = img_byte_arr.getvalue()
        
        # Save to disk if requested
        image_url = ""
        if save_to_disk:
            image_url = self._save_barcode_to_disk(
                barcode_str, 
                image_bytes,
                output_path
            )
        
        return image_bytes, image_url

    def _save_barcode_to_disk(
        self, 
        barcode_str: str, 
        image_data: bytes,
        custom_path: Optional[str] = None
    ) -> str:
        """Save barcode image to disk and return URL"""
        filename = f"{barcode_str}.png"
        filepath = os.path.join(custom_path or self.barcode_base_path, filename)
        
        try:
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # Generate the URL
            if custom_path:
                # For custom paths, use a relative URL
                image_url = f"/media/barcodes/{filename}"
            else:
                image_url = f"{self.barcode_base_url}/{filename}"
            
            logger.info(f"Barcode image saved to: {filepath}")
            return image_url
        except Exception as e:
            logger.error(f"Failed to save barcode image: {str(e)}")
            raise

    @staticmethod
    def verify_code_relationship(instance) -> bool:
        """Verify that unique_code correctly signs the barcode"""
        # Get the UUID field (different names in different models)
        uuid_value = getattr(instance, 'uuid', None) or getattr(instance, 'id', None)
        
        if not uuid_value or not instance.barcode or not instance.unique_code:
            return False
            
        expected_unique = hashlib.blake2b(
            instance.barcode.encode(),
            key=str(uuid_value).encode(),  # Use UUID as key
            digest_size=8
        ).hexdigest().upper()
        
        return instance.unique_code == expected_unique

    @staticmethod
    def get_public_details(instance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return safe-to-share information for public scanning"""
        return {
            'company': "Tagglabs Experiential PVT. LTD.",
            'address': "Eros City Square Mall, Eros City Square, Eros City, Haryana, India",
            'inventory_name': instance_data.get('name'),
            'inventory_id': instance_data.get('uuid'),
            'sno': instance_data.get('sno'),
            'product_id': instance_data.get('product_id'),
            'project_id': instance_data.get('project_id'),
            'employee_name': instance_data.get('employee_name'),
            'status': instance_data.get('status'),
            'contact': 'inventory@tagglabs.com',
            'project_name': instance_data.get('project_name'),
            'event_date': instance_data.get('event_date'),
            'client_name': instance_data.get('client_name')
        }

    @staticmethod
    def get_private_details(instance, requester: Any) -> Dict[str, Any]:
        """Return full details for authorized users"""
        base_details = BarcodeGenerator.get_public_details(instance)

        if requester.role in ['admin', 'owner']:
            return {
                **base_details,
                'setup_date': str(instance.setup_date) if instance.setup_date else None,
                'poc': instance.poc,
                'location': instance.location,
                'submitted_by': instance.submitted_by,
                'system_ids': {
                    'uuid': instance.uuid,
                    'unique_code': instance.unique_code
                }
            }
        elif requester.role == 'staff':
            return {
                **base_details,
                'location': instance.location,
                'last_updated': str(instance.updated_at),
                'project_name': instance.project_name
            }
        return base_details

    @staticmethod
    def validate_project_id(project_id: str) -> str:
        """Validate project ID format"""
        if not project_id:
            raise ValueError("Project ID must be provided")
        return project_id