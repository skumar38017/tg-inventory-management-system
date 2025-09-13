# backend/app/utils/transparent_barcode.py

# backend/app/utils/transparent_barcode.py

from app.utils.common_imports import *
import uuid
import hashlib
import os
import logging
import random
import string
from typing import Tuple, Dict, Any
from barcode.writer import ImageWriter
import barcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from app import config
import boto3
from botocore.exceptions import ClientError

# Initialize logger
logger = logging.getLogger(__name__)

class TransparentBlackBarsWriter(ImageWriter):
    """Writer that renders solid black bars on a fully transparent background without text."""

    def __init__(self):
        super().__init__()
        self.background = None
        self.foreground = 'black'
        self.module_height = 15
        self.quiet_zone = 6
        self.font_size = 0
        self.text_distance = 0
        self.write_text = False  # Completely disable text writing

    def render(self, code):
        """Render barcode with transparent background and opaque black bars."""
        # Completely disable text functionality
        self.text = ""  # Empty text
        self.font = None  # No font
        
        img = super().render(code)

        # Convert to transparent background
        img = img.convert('RGBA')
        pixels = img.getdata()

        new_pixels = []
        for pixel in pixels:
            if pixel[:3] == (255, 255, 255):
                new_pixels.append((255, 255, 255, 0))  # Transparent
            else:
                new_pixels.append((0, 0, 0, 255))  # Opaque black

        img.putdata(new_pixels)
        return img

    # Override text-related methods to prevent any text rendering
    def _paint_text(self, xpos, ypos):
        """Override to completely disable text painting"""
        pass

    def calculate_text_size(self, text):
        """Override to return zero size"""
        return 0, 0

    def get_text_width(self, text):
        """Override to return zero width"""
        return 0

    def get_text_height(self, text):
        """Override to return zero height"""
        return 0

class DynamicBarcodeGenerator:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_S3_REGION_NAME
        )
        self.bucket_name = config.AWS_STORAGE_BUCKET_NAME
        self.barcode_folder = config.AWS_S3_BUCKET_FOLDER_PATH_BARCODE
        self.public_api_url = config.PUBLIC_API_URL
        self.barcode_type = 'code128'

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
                'dpi': 300,
                'write_text': False,  # Explicitly disable text
                'text': ''  # Empty text
            })

            # Add barcode number text at bottom
            img_bytes.seek(0)
            img = Image.open(img_bytes)
            
            # Create new image with extra space for text
            text_height = 20
            new_img = Image.new('RGBA', (img.width, img.height + text_height), (255, 255, 255, 0))
            new_img.paste(img, (0, 0))
            
            # Add text
            draw = ImageDraw.Draw(new_img)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            text_bbox = draw.textbbox((0, 0), barcode_value, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (new_img.width - text_width) // 2
            text_y = img.height + 1
            
            draw.text((text_x, text_y), barcode_value, fill=(0, 0, 0, 255), font=font)
            
            # Convert back to bytes
            final_bytes = BytesIO()
            new_img.save(final_bytes, format='PNG')

            return barcode_value, unique_code, final_bytes.getvalue()

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
                secondary_identifier.upper().startswith(('wireless', 'microphone', 'plastic'))):
                # If secondary identifier looks like a name, swap the parameters
                primary_identifier, secondary_identifier = secondary_identifier, primary_identifier
                logger.warning(f"Auto-corrected swapped parameters. New primary: '{primary_identifier}', secondary: '{secondary_identifier}'")

            # ----- FORMATTING LOGIC -----
            # Format inventory name (lowercase with underscores)
            clean_primary = primary_identifier.replace(' ', '_').lower()
            # Format inventory ID (uppercase alphanumeric)
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
                # Match QR code pattern exactly (just without "_qr" suffix)
                filename = f"{clean_primary}{clean_secondary}_barcode.png"
                barcode_path = inventory_type  # This is send by user [entry, assign, to_event, from_event, wastage]
            
            # Final sanitization
            filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '.'))
            
            # ----- SAVE TO S3 -----
            s3_key = f"{self.barcode_folder}/{barcode_path}/{filename}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=barcode_png,
                ContentType='image/png',
                # ACL='public-read'  # Make the object publicly accessible
            )
            
            # Generate public URL
            s3_url = f"https://{self.bucket_name}.s3.{config.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
            
            return s3_url

        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}", exc_info=True)
            raise ValueError(f"S3 upload failed: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to save barcode image: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to save barcode image: {str(e)}")