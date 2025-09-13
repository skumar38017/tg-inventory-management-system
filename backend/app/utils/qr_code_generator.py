#  backend/app/utils/qr_code_generator.py

from app.utils.common_imports import *
import urllib.request
from urllib.parse import urlparse
from qrcode.image.svg import SvgImage
import logging
import boto3
from botocore.exceptions import ClientError
from PIL import Image, ImageDraw, ImageFont
import os

# Initialize logger
logger = logging.getLogger(__name__)

class QRCodeGenerator:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_S3_REGION_NAME
        )
        self.bucket_name = config.AWS_STORAGE_BUCKET_NAME
        self.qr_folder = config.AWS_S3_BUCKET_FOLDER_PATH_QR
        self.public_api_url = config.PUBLIC_API_URL

    def generate_qr_code(
        self,
        data: str,
        inventory_id: str,
        inventory_name: str,
        size: int = 10,
        border: int = 4,
        error_correction: str = "H",
        qr_color: str = "black",
        save_to_disk: bool = True,
        inventory_type: str = None
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
        try:
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

            # Add icon in center of QR code
            try:
                # Try to load icon.png from backend/app/public folder
                icon_path = config.ICON_PATH
                if os.path.exists(icon_path):
                    icon = Image.open(icon_path).convert("RGBA")
                    # Resize icon to be smaller to maintain QR code scannability (1/8 of QR code size)
                    icon_size = min(img.width, img.height) // 8
                    icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                    
                    # Add white background circle for better visibility
                    circle_size = icon_size + 4
                    circle = Image.new('RGBA', (circle_size, circle_size), (255, 255, 255, 255))
                    circle_x = (img.width - circle_size) // 2
                    circle_y = (img.height - circle_size) // 2
                    img.paste(circle, (circle_x, circle_y), circle)
                    
                    # Calculate center position for icon
                    icon_x = (img.width - icon_size) // 2
                    icon_y = (img.height - icon_size) // 2
                    
                    # Paste icon onto QR code
                    img.paste(icon, (icon_x, icon_y), icon)
            except Exception as e:
                logger.warning(f"Could not add icon to QR code: {e}")

            # Add inventory name text at bottom-center
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            except:
                font = ImageFont.load_default()
            
            # Calculate text dimensions
            temp_draw = ImageDraw.Draw(img)
            text_bbox = temp_draw.textbbox((0, 0), inventory_name, font=font)
            text_height = text_bbox[3] - text_bbox[1] + 10  # Add padding
            
            # Create new image with space for text
            new_img = Image.new('RGBA', (img.width, img.height + text_height), (255, 255, 255, 0))
            new_img.paste(img, (0, 0))
            
            # Add text at bottom-center
            draw = ImageDraw.Draw(new_img)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (new_img.width - text_width) // 2
            text_y = img.height + 1  # 5px padding from QR code
            
            draw.text((text_x, text_y), inventory_name, fill=(0, 0, 0, 255), font=font)

            # Save to bytes
            img_byte_arr = io.BytesIO()
            new_img.save(img_byte_arr, format='PNG')
            image_bytes = img_byte_arr.getvalue()

            # Generate filename and URL
            filename = f"{inventory_name.replace(' ', '_').lower()}{inventory_id}_qr.png"
            filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
            qr_path = inventory_type  # This is send by user [entry, assign, to_event, from_event, wastage]
            
            # Upload to S3
            s3_key = f"{self.qr_folder}/{qr_path}/{filename}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=image_bytes,
                ContentType='image/png'
            )
            
            # Generate public URL
            qr_url = f"https://{self.bucket_name}.s3.{config.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"

            return image_bytes, filename, qr_url
        
        except Exception as e:
            logger.error(f"QR code generation failed: {str(e)}", exc_info=True)
            raise ValueError(f"QR code generation failed: {str(e)}")

    def generate_qr_content(self, instance_data: Union[Dict, object]) -> str:
        """Generate QR code content as a direct API URL"""
        # Handle both dictionary and object access
        name = instance_data['inventory_name'] if isinstance(instance_data, dict) else instance_data.inventory_name
        inventory_id = instance_data['inventory_id'] if isinstance(instance_data, dict) else instance_data.inventory_id
        inventory_type = instance_data['inventory_type'] if isinstance(instance_data, dict) else instance_data.inventory_type
        
        encoded_name = urllib.parse.quote(name)
        return f"{self.public_api_url}/api/v1/scan/{encoded_name}{inventory_id}/{inventory_type}/"