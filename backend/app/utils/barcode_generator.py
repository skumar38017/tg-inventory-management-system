# backend/app/utils/transparent_barcode.py

from backend.app.utils.common_imports import *
import uuid
import hashlib
import os
import logging
import random
import string
from typing import Tuple, Dict, Any
from barcode.writer import ImageWriter
import barcode
from PIL import Image
from io import BytesIO
from backend.app import config

# Initialize logger
logger = logging.getLogger(__name__)

class TransparentBlackBarsWriter(ImageWriter):
    """Writer that renders solid black bars on a fully transparent background without text."""

    def __init__(self):
        super().__init__()
        self.background = None  # No background
        self.foreground = 'black'  # Solid black bars
        self.module_height = 15
        self.quiet_zone = 6
        self.font_size = 0  # No text
        self.text_distance = 0  # No text

    def render(self, code):
        """Render barcode with transparent background and opaque black bars."""
        img = super().render(code)

        # Ensure image is in RGBA mode
        img = img.convert('RGBA')
        pixels = img.getdata()

        # Convert white background to transparent, keep black bars opaque
        new_pixels = []
        for pixel in pixels:
            if pixel[:3] == (255, 255, 255):
                new_pixels.append((255, 255, 255, 0))  # Fully transparent
            else:
                new_pixels.append((0, 0, 0, 255))  # Fully opaque black

        img.putdata(new_pixels)
        return img

class DynamicBarcodeGenerator:
    def __init__(self):
        self.barcode_base_path = config.BARCODE_BASE_PATH
        self.barcode_base_url = config.BARCODE_BASE_URL
        self.public_api_url = config.PUBLIC_API_URL
        os.makedirs(self.barcode_base_path, exist_ok=True)
        self.barcode_type = 'code128'  # Using Code128 for best density

    def _generate_alphanumeric_code(self, length: int = 8) -> str:
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def generate_dynamic_barcode(self, record_data: Dict[str, Any]) -> Tuple[str, str, bytes]:
        try:
            # Deterministic 12-digit numeric code from hash
            record_hash = hashlib.sha256(str(sorted(record_data.items())).encode()).hexdigest()
            barcode_value = ''.join([c for c in record_hash if c.isdigit()])[:13]

            # Unique human-readable verification code
            unique_code = self._generate_alphanumeric_code(13)

            # Generate barcode using transparent writer
            barcode_class = barcode.get_barcode_class(self.barcode_type)
            writer = TransparentBlackBarsWriter()
            barcode_obj = barcode_class(barcode_value, writer=writer)

            # Render image to PNG bytes
            img_bytes = BytesIO()
            barcode_obj.write(img_bytes, options={
                'module_width': 0.3,
                'module_height': 15,
                'quiet_zone': 6,
                'format': 'PNG',
                'dpi': 300
            })

            return barcode_value, unique_code, img_bytes.getvalue()

        except Exception as e:
            logger.error(f"Barcode generation failed: {str(e)}", exc_info=True)
            raise ValueError(f"Barcode generation failed: {str(e)}")

    def save_barcode_image(self, barcode_png: bytes, primary_identifier: str, secondary_identifier: str, inventory_type: str = None) -> str:    
        try:
            # Debug log to verify inputs
            logger.debug(f"Original inputs - primary: '{primary_identifier}', secondary: '{secondary_identifier}', type: '{inventory_type}'")

            # ----- DEFENSIVE CHECKS -----
            # Auto-correct swapped parameters if detected (only for regular inventory)
            if (inventory_type == 'inventory' and 
                secondary_identifier and 
                isinstance(secondary_identifier, str) and 
                secondary_identifier.lower().startswith(('wireless', 'microphone', 'plastic'))):
                # If secondary identifier looks like a name, swap the parameters
                primary_identifier, secondary_identifier = secondary_identifier, primary_identifier
                logger.warning(f"Auto-corrected swapped parameters. New primary: '{primary_identifier}', secondary: '{secondary_identifier}'")

            # ----- FORMATTING LOGIC -----
            # Clean and format the identifiers
            clean_primary = primary_identifier.replace(' ', '_').lower()
            clean_secondary = ''.join(c for c in secondary_identifier.upper() if c.isalnum())
            
            # Determine filename based on inventory type
            if inventory_type == 'assignment_inventory':
                filename = f"assignment_{clean_primary}_{clean_secondary}.png"
            elif inventory_type == 'wastage_inventory':
                filename = f"wastage_{clean_primary}_{clean_secondary}.png"
            elif inventory_type == 'to_event_inventory':
                filename = f"to_event_{clean_primary}_{clean_secondary}.png"
            elif inventory_type == 'from_event_inventory':
                filename = f"from_event_{clean_primary}_{clean_secondary}.png"
            else:
                # Default case for regular inventory
                filename = f"{clean_primary}{clean_secondary}.png"
            
            # Remove any remaining special characters (keeps only alnum, _, and .)
            filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '.'))
            
            # ----- SAVE FILE -----
            filepath = os.path.join(self.barcode_base_path, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb') as f:
                f.write(barcode_png)

            return f"{self.public_api_url}{self.barcode_base_url}/{filename}"

        except Exception as e:
            logger.error(f"Failed to save barcode image: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to save barcode image: {str(e)}")
        