# backend/app/api/endpoints/barcode.py

from backend.app.utils.common_imports import *
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.app.services.barcode_scanner_service import BarcodeScannerService
from backend.app.schema.qrcode_barcode_schema import BarcodeScanResponse, BarcodeScan
from pydantic import ValidationError

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
        summary="Upload barcode scan data",
        description="Upload barcode scan data from request body and return all related data",
        responses={
            200: {"description": "Successfully uploaded barcode scan data and returned records"},
            400: {"description": "No barcode data provided"},
            500: {"description": "Internal server error during processing"}
        },
        tags=["Upload code image (Redis)"]
        )
async def upload_barcode_scan_data(
    request: Request,
    scanner: BarcodeScannerService = Depends(get_barcode_scanner_service)
):
    """
    Process uploaded barcode and return all related data from Redis
    """
    try:
        barcode_data = await request.json()
        if not barcode_data:
            raise HTTPException(status_code=400, detail="No barcode data provided")
        
        if not barcode_data.get("barcode_value"):
            raise HTTPException(
                status_code=400,
                detail="barcode_value is required"
            )
        
        return await scanner.scan_and_fill_details(barcode_data["barcode_value"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing barcode upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )