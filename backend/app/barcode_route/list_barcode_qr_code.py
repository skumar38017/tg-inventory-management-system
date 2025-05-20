
# backend/app/api/endpoints/list_barcode_qr_code.py
from backend.app.utils.common_imports import *
from backend.app.services.list_barcode_qrcode_service import BarcodeQrCodeService
from backend.app.schema.qrcode_barcode_schema import BarcodeQrCodeResponse

def get_barcode_qr_code_service(
        redis: aioredis.Redis = Depends(get_redis_dependency)
) -> BarcodeQrCodeService:
    return BarcodeQrCodeService(redis)

router = APIRouter()

@router.get(
    "/list-barcode-qrcode/", 
    response_model=List[BarcodeQrCodeResponse],
    status_code=200,
    summary="List all barcode QR codes",
    description="List all barcode QR codes stored in Redis",
    responses={
        200: {"description": "Successfully returned all barcode QR codes"},
        500: {"description": "Internal server error"}
    },
    tags=["List Barcode QR Codes"]
)
async def list_barcode_qr_code(
    db: AsyncSession = Depends(get_async_db),
    service: BarcodeQrCodeService = Depends(get_barcode_qr_code_service)
):
    """List all barcode QR codes from Redis"""
    return await service.list_all(db)