# backend/app/curd/homePage/entryinventory/create_inventory.py

from app.utils.common_imports import *

from app.models.entry_inventory_model import EntryInventory
from app.schema.entry_inventory_schema import (
    EntryInventoryCreate, 
)
from app.interface.entry_inverntory_interface import EntryInventoryInterface



class CreateInventoryService(EntryInventoryInterface):
    """Implementation of EntryInventoryInterface with async operations"""
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.qr_generator = QRCodeGenerator()
        self.InventoryUpdater = InventoryUpdater(redis_client)
        self.barcode_generator = DynamicBarcodeGenerator()
        self.base_url = config.BASE_URL

# ------------------------------------------------------------------------------------------------------------------------------------------------
#  inventory entries directly to local databases  (Redis) 
# ------------------------------------------------------------------------------------------------------------------------------------------------

# Create new entry of inventory for which is directly stored in redis
    async def create_entry_inventory(self, db: AsyncSession, inventory_type: str, entry_data: EntryInventoryCreate) -> EntryInventory:
        """
        Create a new inventory entry stored permanently in Redis (no database storage).
        """
        try:
            # Convert input data to dictionary
            if isinstance(entry_data, EntryInventoryCreate):
                inventory_data = entry_data.model_dump(exclude_unset=True)
            else:
                inventory_data = entry_data

            # Handle null/empty date fields
            for date_field in ['purchase_date', 'returned_date']:
                if date_field in inventory_data and inventory_data[date_field] in [None, "", "null", "n/a"]:
                    inventory_data[date_field] = None

            # Generate ID if not provided
            if not inventory_data.get('id'):
                inventory_id = str(uuid.uuid4())
                inventory_data['id'] = inventory_id

            # Set timestamps (server-side only)
            current_time = UTCDateUtils.get_current_datetime()
            inventory_data['updated_at'] = current_time
            inventory_data['created_at'] = current_time 

            # Process and validate boolean fields
            boolean_fields = {
                'on_rent': False,
                'rented_inventory_returned': False,
                'on_event': False,
                'in_office': False,
                'in_warehouse': False
            }

            for field, default_value in boolean_fields.items():
                val = inventory_data.get(field, default_value)
                inventory_data[field] = BaseValidators.validate_boolean_fields(val)

            # Generate barcode if not provided
            if not inventory_data.get('inventory_barcode'):
                # Generate minimal barcode with only bars, code, and unique code
                try:
                    # Generate minimal barcode with only bars, code, and unique code
                    barcode_value, unique_code, barcode_img = self.barcode_generator.generate_dynamic_barcode({
                        'inventory_name': inventory_data['inventory_name'],
                        'inventory_id': inventory_data.get('inventory_id', inventory_id),
                        'type': inventory_type
                    })
                    
                    # Save barcode image
                    barcode_url = self.barcode_generator.save_barcode_image(
                        barcode_img,
                        inventory_data['inventory_name'],
                        inventory_data.get('inventory_id', inventory_id),
                        inventory_type=inventory_type
                        
                    )

                    inventory_data.update({
                        'inventory_barcode': barcode_value,
                        'inventory_unique_code': unique_code,
                        'inventory_barcode_url': barcode_url,
                    })
                except ValueError as e:
                    logger.error(f"Barcode generation failed: {str(e)}")
                    raise HTTPException(status_code=400, detail=str(e))

                try: 
                    # Generate QR code content first
                    qr_content = self.qr_generator.generate_qr_content(inventory_data)

                    # Then generate QR code with the content
                    qr_bytes, filename, qr_url = self.qr_generator.generate_qr_code(
                        data=qr_content,
                        inventory_id=inventory_data['inventory_id'],
                        inventory_name=inventory_data['inventory_name'],
                        inventory_type="inventory"
                    )
                
                    # Add QR code URL to inventory data
                    inventory_data['inventory_qrcode_url'] = qr_url
                except ValueError as e:
                    logger.error(f"QR code generation failed: {str(e)}")
                    raise HTTPException(status_code=400, detail=str(e))
                except Exception as e:
                    logger.error(f"QR code generation failed: {str(e)}", exc_info=True)
                    raise HTTPException(status_code=500, detail=str(e)) 
                
            # Permanent Redis storage (no expiration)
            redis_key = f"inventory:{inventory_data['inventory_name']}{inventory_data['inventory_id']}"
            await self.redis.set(
                redis_key,
                json.dumps(inventory_data, default=str)
            )

            return EntryInventory(**inventory_data)

        except KeyError as ke:
            logger.error(f"Missing required field: {str(ke)}")
            raise HTTPException(status_code=400, detail=f"Missing required field: {str(ke)}")
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encoding error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid inventory data format")
        except Exception as e:
            logger.error(f"Redis storage failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create inventory assignment: {str(e)}"
            )
