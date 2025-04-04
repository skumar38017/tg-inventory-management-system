# backend/app/utils/barcode_generator.py

import uuid
import hashlib
from datetime import datetime, timezone
from typing import Tuple, Dict, Any
from sqlalchemy import event, select
from backend.app.models.to_event_inventry_model import ToEventInventory
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BarcodeGenerator:
    def __init__(self):
        pass  # No initialization needed for static methods

    def generate_linked_codes(self, instance_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Generate cryptographically linked codes for Redis storage
        Returns: (project_barcode, project_barcode_unique_code)
        """
        if 'uuid' not in instance_data or not instance_data['uuid']:
            instance_data['uuid'] = str(uuid.uuid4())
        
        if 'created_at' not in instance_data or not instance_data['created_at']:
            instance_data['created_at'] = datetime.now(timezone.utc).isoformat()

        composite_data = (
            f"{instance_data['uuid']}|{instance_data.get('project_id', '')}|"
            f"{instance_data.get('name', '')[:20]}|{instance_data['created_at']}"
        )

        hash_digest = hashlib.sha256(composite_data.encode()).hexdigest()
        project_barcode = ''.join([d for d in hash_digest if d.isdigit()])[:12].ljust(12, '0')

        project_barcode_unique_code = hashlib.blake2b(
            project_barcode.encode(),
            key=instance_data['uuid'].encode(),
            digest_size=8
        ).hexdigest().upper()

        return project_barcode, project_barcode_unique_code

    @staticmethod
    def verify_code_relationship(instance) -> bool:
        """Verify that project_barcode_unique_code correctly signs the project_barcode"""
        expected_unique = hashlib.blake2b(
            instance.project_barcode.encode(),
            key=instance.uuid.encode(),
            digest_size=8
        ).hexdigest().upper()
        return instance.project_barcode_unique_code == expected_unique

    @staticmethod
    def get_public_details(instance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return safe-to-share information for public scanning"""
        return {
            'company': "Tagglabs Experiential PVT. LTD.",
            'name': instance_data.get('name'),
            'project_id': instance_data.get('project_id'),
            'employee_name': instance_data.get('employee_name'),
            'status': instance_data.get('status'),
            'contact': 'inventory@tagglabs.com',
            'project_name': instance_data.get('project_name'),
            'event_date': instance_data.get('event_date'),
            'client_name': instance_data.get('client_name')
        }

    @staticmethod
    def get_private_details(instance, requester: Any) -> Dict[str, Any]:
        """Return full details for authorized users"""
        base_details = BarcodeGenerator.get_public_details(instance)

        if requester.role in ['admin', 'owner']:
            return {
                **base_details,
                'setup_date': str(instance.setup_date) if instance.setup_date else None,
                'poc': instance.poc,
                'location': instance.location,
                'submitted_by': instance.submitted_by,
                'system_ids': {
                    'uuid': instance.uuid,
                    'unique_code': instance.project_barcode_unique_code
                }
            }
        elif requester.role == 'staff':
            return {
                **base_details,
                'location': instance.location,
                'last_updated': str(instance.updated_at),
                'project_name': instance.project_name
            }
        return base_details

    @staticmethod
    def validate_project_id(project_id: str) -> str:
        """Validate project ID format"""
        if not project_id:
            raise ValueError("Project ID must be provided")
        return project_id

# @event.listens_for(ToEventInventory, 'before_insert')
# def generate_linked_codes(mapper, connection, target):
#     """SQLAlchemy event listener to generate barcodes before insert"""
#     project_barcode, project_barcode_unique_code = BarcodeGenerator.generate_linked_codes(target)
    
#     # Ensure uniqueness
#     while connection.execute(
#         select(ToEventInventory).where(
#             (ToEventInventory.project_barcode == project_barcode) |
#             (ToEventInventory.project_barcode_unique_code == project_barcode_unique_code)
#         )
#     ).first():
#         target.uuid = str(uuid.uuid4())
#         project_barcode, project_barcode_unique_code = BarcodeGenerator.generate_linked_codes(target)
    
#     # Assign codes
#     target.project_barcode = project_barcode
#     target.project_barcode_unique_code = project_barcode_unique_code