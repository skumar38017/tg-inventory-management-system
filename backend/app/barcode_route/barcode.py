# backend/app/api/endpoints/barcode.py

from app.utils.common_imports import *
from fastapi import APIRouter, Depends, HTTPException, Request
from app.services.barcode_scanner_service import BarcodeScannerService
from app.schema.qrcode_barcode_schema import BarcodeScanResponse, BarcodeScan
from pydantic import ValidationError
from fastapi import UploadFile, File
from PIL import Image
from io import BytesIO
import pyzbar.pyzbar as pyzbar

def get_barcode_scanner_service(
        redis: aioredis.Redis = Depends(get_redis_dependency)
)-> BarcodeScannerService:
    return BarcodeScannerService(redis)

router = APIRouter()

@router.get(
        "/scan-barcode/{barcode_value}", 
        response_model=BarcodeScanResponse,
        status_code=200,
        summary="Scan barcode and return all matching records",
        description="Scan barcode and return all matching records from Redis",
        responses={
            200: {"description": "Successfully scanned barcode and returned records"},
            404: {"description": "No records found for the barcode"},
            500: {"description": "Internal server error during scanning"}
        },
        tags=["Scan Code (Redis)"]
        )
async def scan_barcode(
    request: Request,
    barcode_value: str,
    db: AsyncSession = Depends(get_async_db),
    scanner: BarcodeScannerService = Depends(get_barcode_scanner_service)
):
    """Scan barcode and return all matching record data from Redis"""
    return await scanner.scan_and_fill_details(db,barcode_value)

@router.post(
    "/upload-barcode/", 
    response_model=BarcodeScanResponse,
    status_code=200,
    summary="Upload barcode image",
    description="Upload barcode image and return matching records from Redis",
    responses={
        200: {"description": "Successfully decoded barcode and returned records"},
        400: {"description": "Invalid image or no barcode found"},
        404: {"description": "No records found for the decoded barcode"},
        500: {"description": "Internal server error during processing"}
    },
    tags=["Upload code image (Redis)"]
)
async def upload_barcode_image(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    file: UploadFile = File(...),
    scanner: BarcodeScannerService = Depends(get_barcode_scanner_service)
):
    """
    Process uploaded barcode image, decode it, and return matching records from Redis
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "Invalid file type - only images are accepted")
        
        # Read and process image
        contents = await file.read()
        
        try:
            # Decode barcode from image
            img = Image.open(BytesIO(contents))
            decoded_objects = pyzbar.decode(img)
            
            if not decoded_objects:
                raise HTTPException(400, "No barcode found in the image")
            
            # Get the first barcode value
            barcode_value = decoded_objects[0].data.decode('utf-8')
            
            if not barcode_value:
                raise HTTPException(400, "Could not decode barcode value")
            
            logger.info(f"Decoded barcode: {barcode_value}")
            
            # Search Redis for matching records
            return await scanner.scan_and_fill_details(db, barcode_value)
            
        except HTTPException:
            raise
        except Exception as decode_error:
            logger.error(f"Barcode decoding failed: {str(decode_error)}")
            raise HTTPException(400, "Failed to process barcode image")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing barcode upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )