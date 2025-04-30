# backend/app/utils/qr_code_generator.py

import qrcode
import io
import logging
import os
from typing import Tuple, Dict
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from backend.app import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class QRCodeGenerator:
    def __init__(self):
        # Define the base path for barcode images
        self.qrcode_base_path = config.QRCODE_BASE_PATH
        self.qrcode_base_url = config.QRCODE_BASE_URL
        self.public_api_url = config.PUBLIC_API_URL

        # Ensure the directory exists
        os.makedirs(self.qrcode_base_path, exist_ok=True)

    def generate_qr_code(
        self,
        data: str,
        inventory_id: str,
        inventory_name: str,
        style: str = "default",
        size: int = 10,
        border: int = 4,
        error_correction: str = "H",
        save_to_disk: bool = True
    ) -> Tuple[bytes, str, str]:
        """
        Generate a QR code image with optional styling
        Args:
            data: The data to encode in the QR code
            inventory_id: ID of the inventory item for URL generation
            inventory_name: Name of the inventory item for filename
            style: Style of QR code ("default", "rounded", "gradient")
            size: Size of the QR code (1-40)
            border: Border size in modules
            error_correction: Error correction level (L, M, Q, H)
            save_to_disk: Whether to save the image to disk
        Returns:
            Tuple of (image_bytes, filename, qr_url)
        """
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction}"),
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create image based on style
        if style == "rounded":
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                eye_drawer=RoundedModuleDrawer(radius_ratio=1.2)
            )
        elif style == "gradient":
            img = qr.make_image(
                image_factory=StyledPilImage,
                color_mask=RadialGradiantColorMask(
                    center_color=(70, 130, 180),  # Steel blue
                    edge_color=(25, 25, 112)     # Midnight blue
                )
            )
        else:
            img = qr.make_image(
                fill_color="black",
                back_color="white"
            )

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        image_bytes = img_byte_arr.getvalue()

        # Generate filename based on inventory name (sanitized)
        filename = f"{inventory_name.replace(' ', '_').lower()}.png"
        filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
        
        # Generate URL based on inventory ID
        qr_url = f"{self.qrcode_base_url}/{inventory_id}_qr.png"

        # Save to disk if requested
        if save_to_disk:
            os.makedirs(self.qrcode_base_path, exist_ok=True)
            filepath = os.path.join(self.qrcode_base_path, filename)
            try:
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                logger.info(f"QR code saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save QR code: {str(e)}")
                raise

        return image_bytes, filename, qr_url

    def generate_qr_content(self, instance_data: Dict) -> str:
        """
        Generate standardized content for QR codes
        Returns formatted string with all relevant data
        """
        return (
            f"ID: {instance_data.get('id', '')}\n"
            f"Name: {instance_data.get('inventory_name', '')}\n"
            f"Status: {instance_data.get('status', 'active')}\n"
            f"Created: {instance_data.get('created_at', '')}"
        )

    def generate_qr_url(self,inventory_id: str) -> str:
        """
        Generate the QR code URL without creating the image
        Args:
            inventory_id: ID of the inventory item
        Returns:
            The full QR code URL (based on ID)
        """
        return f"{config.QRCODE_BASE_URL}/{inventory_id}_qr.png"