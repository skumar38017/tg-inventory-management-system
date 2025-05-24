# backend/app/services/barcode_scanner_service.py

from app.utils.common_imports import *
from app.interface.barcode_scanner_interface import BarcodeScannerInterface
from app.schema.qrcode_barcode_schema import BarcodeScan, BarcodeScanResponse
import json

class BarcodeScannerService(BarcodeScannerInterface):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.key_patterns = [
            "inventory:*",
            "wastage_inventory:*",
            "from_event_inventory:*",
            "to_event_inventory:*",
            "assignment:*"
        ]

    async def scan_and_fill_details(self,  db: AsyncSession , barcode_value: str) -> Dict[str, Any]:
        """
        Scan barcode across all relevant Redis key patterns and return matching records
        Args:
            barcode_value: Scanned barcode value
        Returns:
            BarcodeScanResponse containing all matching records from different categories
        """
        try:
            matching_records = []
            allowed_fields = set(BarcodeScan.model_fields.keys())
            
            # Search across all key patterns
            for pattern in self.key_patterns:
                async for key in self.redis.scan_iter(pattern):
                    json_data = await self.redis.get(key)
                    if not json_data:
                        continue
                        
                    try:
                        record = json.loads(json_data)
                        # Check multiple possible barcode fields
                        if (record.get("inventory_barcode") == barcode_value or 
                            record.get("barcode_value") == barcode_value):
                            # Filter and standardize the record
                            filtered_record = {
                                k: v for k, v in record.items() 
                                if k in allowed_fields
                            }
                            
                            try:
                                validated_data = BarcodeScan(**filtered_record)
                                matching_records.append(validated_data)
                            except ValidationError as e:
                                logger.warning(f"Validation failed for record {key}: {str(e)}")
                                continue
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON for key {key}: {str(e)}")
                        continue
            
            if not matching_records:
                raise HTTPException(
                    status_code=404,
                    detail=f"No records found for barcode: {barcode_value}"
                )
            
            logger.info(f"Found {len(matching_records)} records for barcode: {barcode_value}")
            
            return BarcodeScanResponse(
                items=matching_records,
                total_count=len(matching_records))
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Barcode scan failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process barcode: {str(e)}"
            )