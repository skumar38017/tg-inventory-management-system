# backend/app/api/endpoints/qrcode.py
from backend.app.utils.common_imports import *

from backend.app.schema.qrcode_barcode_schema import InventoryQrCodeResponse
from backend.app.services.qrcode_service import QRCodeService
from fastapi import Request
# Set up the router
router = APIRouter()

# Set up templates
templates = Jinja2Templates(directory="backend/app/templates")

@router.get("/scan/{qr_data}/",
    response_class=HTMLResponse,
    response_model=InventoryQrCodeResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    tags=["Scan Code (Redis)"]
)
async def scan_qrcode(
    qr_data: str,
    request: Request,
    redis_client: aioredis.Redis = Depends(get_redis_dependency)
) -> InventoryQrCodeResponse:
    """
    Public endpoint for QR code scanning with rate limiting
    Uses Redis-only backend with enhanced lookup capabilities
    
    Supports scanning by:
    - Full Redis key (inventory:LED Screen PanelINV001)
    - Inventory ID (INV001)
    - Product ID (PRD001)
    - UUID (7a3e3f94-e87c-4853-b793-411a7bd3e270)
    - Partial matches (LED, Panel, etc.)
    - Pipe-separated formats (name+ID|ID)
    """
    logger.info(f"Starting QR code scan for: {qr_data}")
    try:
        qr_service = QRCodeService(redis_client)

        # First try to decode URL if present
        if qr_data.startswith(('http://', 'https://')):
            qr_data = qr_service._extract_qr_data_from_url(qr_data) or qr_data
        
        # Standardize the input format
        processed_data = qr_service._standardize_qr_input(qr_data)

        # First try exact match
        logger.info("Trying exact match...")
        item = await qr_service.get_inventory_item_by_qr(processed_data)
        
        if not item:
            # Try extracting ID (e.g., "INV002" from "Steel RodINV002")
            logger.info("No exact match, trying ID extraction...")
            inventory_id = qr_service._extract_inventory_id(qr_data)
            if inventory_id:
                # Check ID index
                redis_key = await redis_client.get(f"inventory:id:{inventory_id}")
                if redis_key:
                    item_data = await redis_client.get(redis_key)
                    if item_data:
                        item = qr_service._parse_redis_item(item_data)
        
        if not item:
            # Try cleaned input (lowercase, trimmed)
            logger.info("No ID match, trying cleaned input...")
            cleaned_data = qr_data.strip().lower()
            if cleaned_data != qr_data:  # Only retry if different
                item = await qr_service.get_inventory_item_by_qr(cleaned_data)
        
        if not item:
            # Try with inventory prefix
            logger.info("No cleaned match, trying with inventory prefix...")
            if not qr_data.startswith("inventory:"):
                prefixed_data = f"inventory:{qr_data}"
                item = await qr_service.get_inventory_item_by_qr(prefixed_data)
        
        if not item:
            # Final fallback: wildcard search by ID
            logger.info("No prefix match, trying wildcard search...")
            inventory_id = qr_service._extract_inventory_id(qr_data)
            if inventory_id:
                pattern = f"inventory:*{inventory_id}*"
                cursor = "0"
                while True:
                    cursor, keys = await redis_client.scan(
                        cursor=cursor,
                        match=pattern,
                        count=100
                    )
                    for key in keys:
                        item_data = await redis_client.get(key)
                        if item_data:
                            item = qr_service._parse_redis_item(item_data)
                            if item:
                                break
                    if cursor == "0" or item:
                        break
        
        if not item:
            logger.warning("Item not found after all lookup attempts")
            return templates.TemplateResponse(
                "record.html",
                {
                    "request": request, 
                    "company": "Tagglabs Experiential PVT. LTD.",
                    "type": "inventory",
                    "error": "Item not found in Redis. Try scanning with: inventory ID, product ID, or item name",
                    "qr_code_url": ""
                }
            )
        
        logger.info("Item found, mapping to response schema...")
        response_data = qr_service.map_to_response_schema(item)
        
        # Convert to dict and add timestamp
        response_data_dict = response_data.dict()
        response_data_dict["now"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add QR code URL - using dictionary access
        response_data_dict["qr_code_url"] = f"{config.PUBLIC_API_URL}{config.QRCODE_BASE_URL}/{item['inventory_name'].replace(' ', '_').lower()}{item['inventory_id']}_qr.png"
        logger.info(f"Successfully returned response for {qr_data}")
        
        return templates.TemplateResponse(
            "record.html",
            {
                "request": request, 
                **response_data_dict
            }
        )
        
    except Exception as e:
        logger.error(f"QR code scanning failed: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "record.html",
            {
                "request": request,
                "company": "Tagglabs Experiential PVT. LTD.",
                "type": "inventory",
                "error": f"Internal server error: {str(e)}",
                "qr_code_url": ""
            }
        )

@router.post("/upload/", response_model=InventoryQrCodeResponse,
            tags=["Upload code image (Redis)"]
            )
async def upload_qrcode(
    file: UploadFile = File(...),
    redis_client: aioredis.Redis = Depends(get_redis_dependency)
) -> InventoryQrCodeResponse:
    
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "Invalid file type")
            
        # Read and process image
        contents = await file.read()
        img = Image.open(BytesIO(contents))
        
        # Convert to grayscale if needed
        if img.mode != 'L':
            img = img.convert('L')
            
        # Enhance contrast
        img = ImageEnhance.Contrast(img).enhance(1.5)
        
        # Decode QR code
        decoded_objects = pyzbar.decode(img)
        if not decoded_objects:
            # Try inverted colors
            inverted_img = Image.eval(img, lambda x: 255 - x)
            decoded_objects = pyzbar.decode(inverted_img)
            if not decoded_objects:
                raise HTTPException(400, "Could not decode QR code")
        
        # Get decoded data
        decoded_data = decoded_objects[0].data.decode('utf-8').strip()
        logger.info(f"Decoded QR content: {decoded_data}")
        
        # Standardize the decoded data
        qr_service = QRCodeService(redis_client)
        processed_data = qr_service._standardize_qr_input(decoded_data)

        # Clean and process the data
        if decoded_data.startswith('http'):
            # Extract last part of URL if it's a URL
            decoded_data = decoded_data.split('/')[-1]
            
        # Remove any file extensions if present
        decoded_data = decoded_data.replace('.png', '').replace('.jpg', '')
        
        # Try scanning with the decoded data
        return await scan_qrcode(processed_data, redis_client)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(500, "Failed to process QR code")