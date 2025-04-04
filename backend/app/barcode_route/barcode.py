#  backend/app/models/barcode.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# from backend.app.auth import get_current_user
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.database.base import get_db
from fastapi_limiter.depends import RateLimiter
import secrets
import hashlib
from datetime import datetime, timezone

router = APIRouter()

@router.get("/scan/{barcode}", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def scan_barcode(
    barcode: str,
    # current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint for barcode scanning with access control. The rate limit is 5 scans per minute.
    This endpoint scans a barcode and verifies its authenticity. Returns the details of the
    item associated with the barcode after verifying its signature and access level.
    """
    # Query the database for the entry by barcode
    item = await db.execute(
        select(EntryInventory).where(EntryInventory.bar_code == barcode)
    )
    item = item.scalars().first()  # Get the first matching item
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify the barcode relationship (e.g., check signature)
    if not item.verify_code_relationship():
        raise HTTPException(status_code=400, detail="Invalid barcode signature")
    
    # Return the private details of the item to the current user based on access control
    # return item.get_private_details(current_user)

def generate_qr_code(item, access_level='public'):
    """
    Generates a QR code URL for the item. 
    - 'public' access level: Public QR link to scan the item
    - 'internal' access level: Internal QR link with an access token for more sensitive info.
    """
    # Construct the appropriate URL for the QR code based on access level
    qr_data = {
        'public': f"https://api.example.com/scan/{item.bar_code}",
        'internal': f"https://internal.example.com/scan/{item.bar_code}?token={generate_scan_token(item)}"
    }
    
    return qr_data.get(access_level, qr_data['public'])  # Return the corresponding URL

def generate_scan_token(item):
    """
    Generates a secure token for internal access to the item.
    This token should be used to validate access to sensitive item details.
    """
    # For example, create a secure token using the item ID and a secret
    token_data = f"{item.bar_code}-{secrets.token_hex(16)}"
    return hashlib.sha256(token_data.encode('utf-8')).hexdigest()  # Return hashed token

