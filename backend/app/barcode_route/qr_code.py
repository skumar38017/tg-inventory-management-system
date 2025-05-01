# backend/app/api/endpoints/qrcode.py

from backend.app.database.redisclient import get_redis_dependency
from redis import asyncio as aioredis
from fastapi import APIRouter, HTTPException, Depends
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.utils.qr_code_generator import QRCodeGenerator
from backend.app.schema.qrcode_barcode_schema import InventoryQrCodeResponse
from backend.app.services.qrcode_service import QRCodeService
import json
import logging
from fastapi_limiter.depends import RateLimiter
from typing import Optional
import qrcode
from PIL import ImageEnhance
from pyzbar import pyzbar
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)
router = APIRouter()

# Set up the router
router = APIRouter()

@router.get("/scan/{qr_data}",
    response_model=InventoryQrCodeResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)

async def scan_qrcode(qr_data: str, redis_client: aioredis.Redis = Depends(get_redis_dependency)) -> InventoryQrCodeResponse:
    """
    Public endpoint for QR code scanning with rate limiting
    Uses Redis-only backend
    Supports scanning by:
    - Full Redis key (inventory:LED Screen PanelINV001)
    - Inventory ID (INV001)
    - Product ID (PRD001)
    - UUID (7a3e3f94-e87c-4853-b793-411a7bd3e270)
    - Partial matches (LED, Panel, etc.)
    """
    logger.info(f"Starting QR code scan for: {qr_data}")
    try:
        qr_service = QRCodeService(redis_client)
        
        logger.info("Trying exact matches...")
        item = await qr_service.get_inventory_item_by_qr(qr_data)
        
        if not item:
            logger.info("No exact match, trying cleaned input...")
            cleaned_data = qr_data.strip().lower()
            item = await qr_service.get_inventory_item_by_qr(cleaned_data)
            
            if not item:
                logger.info("No cleaned match, trying with inventory prefix...")
                if not qr_data.startswith("inventory:"):
                    prefixed_data = f"inventory:{qr_data}"
                    item = await qr_service.get_inventory_item_by_qr(prefixed_data)
        
        if not item:
            logger.warning("Item not found after all lookup attempts")
            raise HTTPException(
                status_code=404,
                detail="Item not found in Redis. Try scanning with: inventory ID, product ID, or item name"
            )
        
        logger.info("Item found, mapping to response schema...")
        response_data = qr_service.map_to_response_schema(item)
        logger.info(f"Returning response for {qr_data}")
        
        return response_data
        
    except HTTPException:
        logger.error("HTTPException in scan_qrcode", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"QR code scanning failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )    

@router.post("/upload/",
    response_model=InventoryQrCodeResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
async def upload_qrcode(
    file: UploadFile = File(...),
    redis_client: aioredis.Redis = Depends(get_redis_dependency)
) -> InventoryQrCodeResponse:
    """
    Endpoint for uploading QR code images
    Returns inventory data matching the scanned QR code content
    
    Supports:
    - PNG, JPEG, GIF images
    - Both standard and inverted color QR codes
    - Multiple QR codes in single image (uses first found)
    - Automatic image preprocessing for better detection
    """
    try:
        # Validate file type
        if file.content_type not in ['image/png', 'image/jpeg', 'image/gif', 'image/webp']:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PNG, JPEG, or GIF"
            )

        # Read and decode the image
        contents = await file.read()
        
        try:
            # Preprocess image for better QR detection
            img = Image.open(BytesIO(contents))
            
            # Convert to grayscale if needed
            if img.mode != 'L':
                img = img.convert('L')
            
            # Enhance contrast
            img = ImageEnhance.Contrast(img).enhance(1.5)
            
            # Try multiple QR code libraries if needed
            decoded_data = None
            for decoder in [qrcode.decode, pyzbar.decode]:
                try:
                    result = decoder(img)
                    if result:
                        if isinstance(result, list):  # pyzbar returns list
                            decoded_data = result[0].data.decode('utf-8')
                        else:  # qrcode returns single object
                            decoded_data = result.data.decode('utf-8')
                        break
                except:
                    continue
            
            if not decoded_data:
                raise HTTPException(
                    status_code=400,
                    detail="Could not decode QR code from image"
                )
            
            # Clean and validate the decoded data
            decoded_data = decoded_data.strip()
            if not decoded_data:
                raise HTTPException(
                    status_code=400,
                    detail="Empty QR code content"
                )
            
            # Use the scan endpoint logic
            return await scan_qrcode(decoded_data, redis_client)
            
        except HTTPException:
            raise
        except Exception as decode_error:
            logger.error(f"QR decoding failed: {str(decode_error)}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail="Failed to process QR code image"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR upload failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during QR code processing"
        )