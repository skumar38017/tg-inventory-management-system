# backend/app/services/barcode_scanner_service.py
from backend.app.utils.common_imports import *
from backend.app.interface.barcode_scanner_interface import BarcodeScannerInterface

class BarcodeScannerService(BarcodeScannerInterface):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.base_url = config.BASE_URL

    async def scan_and_fill_details(self, barcode_value: str) -> Dict[str, Any]:
        """
        Scan barcode and return associated record details from Redis
        Args:
            barcode_value: Scanned barcode value
        Returns:
            Dictionary of record details to auto-fill
        """
        try:
            # Look up the record in Redis
            record_key = f"inventory:{barcode_value}"
            record = await self.redis.hgetall(record_key)
            
            if not record:
                raise HTTPException(status_code=404, detail="Record not found in Redis")
            
            # Convert Redis hash to dictionary for auto-filling
            record_data = {
                'id': record.get('id'),
                'name': record.get('name'),
                'barcode': barcode_value,
                'unique_code': record.get('unique_code'),
                'category': record.get('category'),
                'quantity': record.get('quantity', '1'),
                'location': record.get('location'),
                'date_added': record.get('date_added'),
                'inventory_id': record.get('inventory_id'),
                'product_id': record.get('product_id'),
                'material': record.get('material'),
                'manufacturer': record.get('manufacturer'),
                'status': record.get('status'),
                # Add other fields as needed from Redis
            }
            
            logger.info(f"Fetched record data from Redis for barcode: {barcode_value}")
            return record_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis barcode scan failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process barcode from Redis: {str(e)}"
            )