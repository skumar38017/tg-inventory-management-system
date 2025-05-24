# backend/app/services/list_barcode_qrcode_service.py

from app.utils.common_imports import *
from app.interface.barcode_scanner_interface import BarcodeScannerInterface
from app.schema.qrcode_barcode_schema import BarcodeQrCodeResponse
import json

class BarcodeQrCodeService(BarcodeScannerInterface):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def list_all(self, db: AsyncSession) -> Dict[str, Any]:
        try:
            keys = await self.redis.keys("inventory:*")
            results = []
            for key in keys:
                inventory_json = await self.redis.get(key)
                if not inventory_json:
                    continue
                inventory_data = json.loads(inventory_json)
                results.append(BarcodeQrCodeResponse(**inventory_data))
            
            # Sort results by inventory_name a-to-z
            results.sort(key=lambda x: x.inventory_name.lower())
            return results
        except Exception as e:
            logger.error(f"Failed to list barcode QR codes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")