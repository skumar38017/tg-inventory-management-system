#  backend/app/interface/qrcode_interface.py
from typing import List, Optional
from pydantic import BaseModel
from backend.app.schema.qrcode_barcode_schema import InventoryQrCode, InventoryQrCodeResponse

class QRCodeInterface(BaseModel):
    """Interface for QR code operations"""
    def generate_qr_code(self, instance_data: dict, inventory_type: str = None) -> InventoryQrCode:
        """Generate QR code data"""
        raise NotImplementedError

    def generate_qr_code_response(self, instance_data: dict, inventory_type: str = None) -> InventoryQrCodeResponse:
        """Generate QR code response data"""
        raise NotImplementedError
