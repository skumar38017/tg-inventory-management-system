# backend/app/api/endpoints/barcode.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from backend.app.services.barcode_scanner_service import BarcodeScannerService
from backend.app.utils.barcode_generator import TransparentBarcodeGenerator
from backend.app.schema.qrcode_barcode_schema import BarcodeScanResponse

router = APIRouter()

@router.post("/generate-barcode", response_class=FileResponse)
async def generate_transparent_barcode(record_data: dict):
    """Generate transparent barcode for a record"""
    try:
        generator = TransparentBarcodeGenerator()
        barcode_value, unique_code, barcode_image = generator.generate_dynamic_barcode(record_data)
        
        # Save the image temporarily
        filename = f"barcode_{barcode_value}.svg"
        filepath = generator.save_barcode_image(barcode_image, filename)
        
        return FileResponse(
            filepath,
            media_type="image/svg+xml",
            headers={
                "Barcode-Value": barcode_value,
                "Unique-Code": unique_code
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scan-barcode/{barcode_value}", response_model=BarcodeScanResponse)
async def scan_barcode(barcode_value: str, scanner: BarcodeScannerService = Depends()):
    """Scan barcode and return record data"""
    return await scanner.scan_and_fill_details(barcode_value)