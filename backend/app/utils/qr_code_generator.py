#  backend/app/utils/qr_code_generator.py

from backend.app.utils.common_imports import *
import urllib.request
from urllib.parse import urlparse
from qrcode.image.svg import SvgImage
import logging
import boto3
from botocore.exceptions import ClientError

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

            # Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            image_bytes = img_byte_arr.getvalue()

            # Generate filename and URL
            filename = f"{inventory_name.replace(' ', '_').lower()}{inventory_id}_qr.png"
            filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
            
            # Upload to S3
            s3_key = f"{self.qr_folder}/{filename}"
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
        
        encoded_name = urllib.parse.quote(name)
        return f"{self.public_api_url}/api/v1/scan/{encoded_name}{inventory_id}/"