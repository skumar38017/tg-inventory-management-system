# backend/app/api/endpoints/qrcode.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.base import get_db
from backend.app.utils.qr_code_generator import QRCodeGenerator
from backend.app.schema.qrcode_barcode_schema import InventoryQrCodeResponse
import json
from fastapi_limiter.depends import RateLimiter

router = APIRouter()

@router.get("/scan/{qr_data}",
    response_model=InventoryQrCodeResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
async def scan_qrcode(
    qr_data: str,
    db: AsyncSession = Depends(get_db)
    ): -> InventoryQrCodeResponse:
    """
    Public endpoint for QR code scanning with rate limiting
    Returns validated InventoryQrCodeResponse structure
    """
    try:
        # First try to parse as JSON (public QR codes)
        try:
            qr_content = json.loads(qr_data)
            
            # If it's our standard public QR code format
            if isinstance(qr_content, dict) and qr_content.get("company") == "Tagglabs Experiential PVT. LTD.":
                # Validate against our schema
                response_data = InventoryQrCodeResponse(**qr_content)
                return JSONResponse({
                    "status": "success",
                    "type": "public",
                    "data": response_data.model_dump()
                })
                
        except json.JSONDecodeError:
            pass  # Not JSON, proceed with database lookup

        # Database lookup implementation
        item = None  # await get_inventory_item_by_qr(qr_data, db)
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Convert database item to our schema
        try:
            # This mapping depends on your database model structure
            inventory_data = {
                "id": getattr(item, 'id', None),
                "product_id": getattr(item, 'product_id', None),
                "inventory_id": getattr(item, 'inventory_id', None),
                "inventory_name": getattr(item, 'inventory_name', None),
                # ... map all other fields from item to schema
            }
            
            response_data = InventoryQrCodeResponse(**inventory_data)
            
            return JSONResponse({
                "status": "success",
                "type": "database",
                "data": response_data.model_dump()
            })
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            raise HTTPException(status_code=422, detail="Invalid inventory data structure")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR code scanning failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")