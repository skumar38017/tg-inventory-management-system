#  backend/app/interface/qrcode_interface.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schema.qrcode_barcode_schema import InventoryQrCode, InventoryQrCodeResponse
from app.services.qrcode_service import QRCodeService

class QRCodeInterface(BaseModel):
    """Interface for QR code operations"""
    def generate_qr_code(self, instance_data: dict, inventory_type: str = None) -> InventoryQrCode:
        """Generate QR code data"""
        raise NotImplementedError

    def generate_qr_code_response(self, instance_data: dict, inventory_type: str = None) -> InventoryQrCodeResponse:
        """Generate QR code response data"""
        raise NotImplementedError

    def get_inventory_item_by_qr(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """Fetch inventory item by QR code data"""
        raise NotImplementedError

    def map_to_response_schema(self, item_data: Dict[str, Any]) -> InventoryQrCodeResponse:
        """Map raw inventory data to our response schema"""
        raise NotImplementedError