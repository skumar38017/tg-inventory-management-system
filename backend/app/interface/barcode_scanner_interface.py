#  backend/app/interface/barcode_scanner_interface.py
from backend.app.utils.common_imports import *
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.schema.qrcode_barcode_schema import BarcodeQrCodeResponse

class BarcodeScannerInterface:
    async def scan_and_fill_details(self, barcode_value: str) -> Dict[str, Any]:
        """
        Scan barcode and return associated record details from Redis
        Args:
            barcode_value: Scanned barcode value
        Returns:
            Dictionary of record details to auto-fill
        """
        pass    

    async def list_all(self, db: AsyncSession) -> List[BarcodeQrCodeResponse]:
        """List all barcode QR codes"""
        pass