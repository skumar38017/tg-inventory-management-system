#  backend/app/utils/qr_code_generator.py

import qrcode
import io
import logging
import os
from typing import Tuple, Dict
from PIL import Image
from backend.app import config
from typing import Union, Dict
import urllib.request
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class QRCodeGenerator:
    def __init__(self):
        self.qrcode_base_path = config.QRCODE_BASE_PATH
        self.qrcode_base_url = config.QRCODE_BASE_URL
        self.public_api_url = config.PUBLIC_API_URL 
        os.makedirs(self.qrcode_base_path, exist_ok=True)

    def generate_qr_code(
        self,
        data: str,
        inventory_id: str,
        inventory_name: str,
        size: int = 10,
        border: int = 4,
        error_correction: str = "H",
        qr_color: str = "black",
        save_to_disk: bool = True
    ) -> Tuple[bytes, str, str]:
        """
        Generate a simple QR code with transparent background
        Args:
            data: The data to encode
            inventory_id: ID for URL generation
            inventory_name: Name for filename
            size: Size of QR code (1-40)
            border: Border size in modules
            error_correction: Error correction level (L, M, Q, H)
            qr_color: Color of QR code (hex or name)
            save_to_disk: Whether to save the image
        Returns:
            Tuple of (image_bytes, filename, qr_url)
        """
        # Create basic QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction}"),
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create solid color QR code with white background first
        img = qr.make_image(fill_color=qr_color, back_color="white")
        
        # Convert to transparent background
        img = img.convert("RGBA")
        datas = img.getdata()
        
        new_data = []
        for item in datas:
            # Make white pixels transparent
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                new_data.append((255, 255, 255, 0))
            else:
                # Keep colored pixels fully opaque
                new_data.append(item)
        
        img.putdata(new_data)

        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        image_bytes = img_byte_arr.getvalue()

        # Generate filename and URL
        filename = f"{inventory_name.replace(' ', '_').lower()}{inventory_id}_qr.png"
        filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
        qr_url = f"{self.public_api_url}{self.qrcode_base_url}/{filename}"

        # Save to disk if requested
        if save_to_disk:
            filepath = os.path.join(self.qrcode_base_path, filename)
            try:
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                logger.info(f"QR code saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save QR code: {str(e)}")
                raise

        return image_bytes, filename, qr_url

    def generate_qr_content(self, instance_data: Union[Dict, object]) -> str:
        """Generate QR code content as a direct API URL"""
        # Handle both dictionary and object access
        name = instance_data['inventory_name'] if isinstance(instance_data, dict) else instance_data.inventory_name
        inventory_id = instance_data['inventory_id'] if isinstance(instance_data, dict) else instance_data.inventory_id
        
        encoded_name = urllib.parse.quote(name)
        return f"{self.public_api_url}/api/v1/scan/{encoded_name}{inventory_id}/"