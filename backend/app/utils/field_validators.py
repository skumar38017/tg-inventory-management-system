# backend/app/utils/field_validators.py
import re
import json
from datetime import datetime, date, timezone, timedelta
from typing import Optional, Union, Dict, Any
from pydantic import field_validator, model_validator, ValidationInfo, ConfigDict
from enum import Enum
from backend.app.utils.date_utils import UTCDateUtils  # Changed from IndianDateUtils to UTCDateUtils

class BaseValidators:
    """Contains reusable validators that can be inherited by different schemas"""
    
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        json_encoders={
            datetime: lambda v: UTCDateUtils.format_datetime(v),  # Changed to UTC format
            date: lambda v: UTCDateUtils.format_date(v),
            Enum: lambda v: v.value
        }
    )

    # ---------------------------- Generic Field Validators ----------------------------
    @staticmethod
    def empty_string_to_none(v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
        return None if v == "" else v
    
    @staticmethod
    def validate_boolean_fields(v) -> str:
        """Convert boolean values to consistent string representation"""
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return v.lower()
        return "false"

    @staticmethod
    def format_id_field(v: Optional[str], prefix: str) -> Optional[str]:
        """Generic ID formatter that adds prefix if missing and validates format
        
        Rules:
        1. If input is None or empty string, return None
        2. Remove any existing prefix (case insensitive)
        3. Extract all digits from the remaining string
        4. If no digits found, raise ValueError
        5. Combine prefix with extracted digits
        """
        if v is None:
            return None
        
        v = str(v).strip().upper()
        if not v:
            return None
        
        clean_id = re.sub(f'^{prefix}', '', v, flags=re.IGNORECASE)
        digits = re.sub(r'[^\d]', '', clean_id)
        if not digits:
            raise ValueError(f"ID must contain numbers after prefix (input: {v})")
        
        return f"{prefix}{digits}"

    @staticmethod
    def validate_quantity(v) -> Optional[Union[float, int]]:
        """Convert quantity to number, handling strings and empty values"""
        if v is None:
            return None
        if isinstance(v, str):
            if not v.strip():
                return None
            try:
                return float(v)
            except ValueError:
                raise ValueError("Quantity must be a number")
        return v

    @staticmethod
    def validate_whole_number(v) -> Optional[int]:
        """Validate that quantity is a whole number"""
        if v is None:
            return None
        if isinstance(v, str):
            if not v.strip():
                return None
            try:
                return int(float(v))
            except ValueError:
                raise ValueError("Quantity must be a whole number")
        elif isinstance(v, (float, int)):
            return int(v)
        return v

    # ---------------------------- Field Validators ----------------------------
    @field_validator('*', mode='before', check_fields=False)
    def check_empty_strings(cls, v):
        """Generic validator to convert empty strings to None for all fields"""
        return cls.empty_string_to_none(v)
     

    @field_validator('product_id', mode='before', check_fields=False)
    def validate_product_id(cls, v):
        """Standard product ID validator"""
        result = cls.format_id_field(v, 'PRD')
        if result is None:
            return None
        if len(result) > 20:
            raise ValueError("Product ID too long (max 20 chars)")
        return result

    @field_validator('inventory_id', mode='before', check_fields=False)
    def validate_inventory_id(cls, v):
        """Standard inventory ID validator"""
        result = cls.format_id_field(v, 'INV')
        if result is None:
            return None
        if len(result) > 20:
            raise ValueError("Inventory ID too long (max 20 chars)")
        return result

    @field_validator('project_id', mode='before', check_fields=False)
    def validate_project_id(cls, v):
        """Standard project ID validator that ensures format PRJ12345"""
        result = cls.format_id_field(v, 'PRJ')
        if result is None:
            return None
        if len(result) > 20:  # Example length check
            raise ValueError("Project ID too long (max 20 chars)")
        return result

    @field_validator(
        'on_rent', 'rented_inventory_returned', 'on_event', 
        'in_office', 'in_warehouse', 
        mode='before', check_fields=False
    )
    def validate_booleans(cls, v):
        """Standard boolean fields validator"""
        return cls.validate_boolean_fields(v)

    @field_validator(
        'purchase_date', 'returned_date', 'assigned_date', 
        'assignment_return_date', 'receive_date', 'event_date', 
        'wastage_date', 'setup_date', 'to_date', 'from_date',
        mode='before', check_fields=False
    )
    def validate_dates(cls, v):
        """Standard date fields validator"""
        return UTCDateUtils.validate_date_field(v)

    @field_validator(
        'created_at', 'updated_at', 'submission_date',
        mode='before', check_fields=False
    )
    def validate_timestamps(cls, v):
        """Standard datetime fields validator with timezone handling"""
        if isinstance(v, str):
            try:
                dt = UTCDateUtils.parse_datetime(v)  # Changed to UTC
                return UTCDateUtils.format_datetime(dt) if dt else v  # Changed to UTC format
            except ValueError:
                return v
        return UTCDateUtils.validate_datetime_field(v)  # Changed to UTC

    @field_validator(
        'inventory_barcode_url', 'barcode_image_url', 
        'project_barcode_image_url', mode='before', check_fields=False
    )
    def clean_barcode_url(cls, v):
        """Clean barcode URL fields"""
        if v is None:
            return None
        return cls.empty_string_to_none(str(v).replace('\"', ''))

    @field_validator(
        'quantity', 'RecQty', 'per_unit_power', 'total_power',
        mode='before', check_fields=False
    )
    def validate_numeric_fields(cls, v):
        """Standard numeric fields validator"""
        return cls.validate_quantity(v)

    @field_validator('unit', mode='before', check_fields=False)
    def convert_unit_to_string(cls, v):
        """Ensure unit fields are strings"""
        if v is None:
            return None
        return str(v) if not isinstance(v, str) else v

    @field_validator('id', mode='before', check_fields=False)
    def set_id_from_uuid(cls, v, info: ValidationInfo):
        """Set ID from UUID if not provided"""
        if v is None:
            if hasattr(info, 'data') and info.data and 'uuid' in info.data:
                return info.data['uuid']
        return v

    # ---------------------------- Model Validators ----------------------------
    @model_validator(mode='before')
    def handle_timestamps(cls, values: Dict) -> Dict:
        """Special handling for timestamps including typo correction"""
        if not isinstance(values, dict):
            return values
            
        # Skip timestamp handling for create models
        if cls.__name__ in ('EntryInventoryCreate', 'EntryInventoryBase'):
            return values
            
        # Handle created_at typo
        if 'created_at' not in values or values['created_at'] is None:
            if 'cretaed_at' in values and values['cretaed_at'] is not None:
                values['created_at'] = values['cretaed_at']
            else:
                values['created_at'] = UTCDateUtils.get_current_datetime_iso()  # Changed to UTC ISO format
        
        # Always set updated_at to now in UTC
        values['updated_at'] = UTCDateUtils.get_current_datetime_iso()  # Changed to UTC ISO format
            
        return values

    @model_validator(mode='before')
    def validate_date_range(cls, values: Dict) -> Dict:
        """Validate that to_date is after from_date if both exist"""
        if not isinstance(values, dict):
            return values
            
        if 'from_date' in values and 'to_date' in values:
            from_date = values['from_date']
            to_date = values['to_date']
            
            if from_date and to_date:
                if isinstance(from_date, str):
                    from_date = UTCDateUtils.parse_date(from_date)  # Changed to UTC
                if isinstance(to_date, str):
                    to_date = UTCDateUtils.parse_date(to_date)  # Changed to UTC
                
                if from_date and to_date and to_date < from_date:
                    raise ValueError("To date must be after From date")
        return values

    # ---------------------------- Special Methods ----------------------------
    @classmethod
    def from_redis(cls, redis_data: str):
        """Create instance from Redis JSON data"""
        data = json.loads(redis_data)
        return cls(**data)

    def to_orm_dict(self):
        """Convert to dictionary suitable for SQLAlchemy model"""
        data = self.model_dump(exclude={'inventory_items', 'created_at', 'updated_at'})
        if hasattr(self, 'inventory_items'):
            data['items'] = [item.model_dump(exclude={'project_id'}) for item in self.inventory_items]
        return data
    # ---------------------------- Common Enums ----------------------------
class StatusEnum(str, Enum):
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    INHOUSE = "In House"
    OUTSIDE = "Outside"
    RETURNED = "Returned"
    REJECTED = "Rejected"
    PENDING = "Pending"
    FAILED = "Failed"
    APPROVED = "Approved"
    UNDER_REVIEW = "Under Review"
    ON_HOLD = "On Hold"
    DELIVERED = "Delivered"
    SHIPPED = "Shipped"
    IN_TRANSIT = "In Transit"
    DELAYED = "Delayed"
    CLOSED = "Closed"
    OPEN = "Open"
    EXPIRED = "Expired"
    WITHDRAWN = "Withdrawn"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    RESERVED = "Reserved"
    WAITLISTED = "Waitlisted"
    ADJUSTED = "adjusted"
    ALLOCATED = "Allocated"
    ANALYZED = "Analyzed"
    ANALYZED_COMPLETED = "Analyzed Completed"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_REJECTED = "appeal_rejected"
    APPROVED_BY_HIGHER_AUTHORITY = "Approved By Higher Authority"
    ARCHIVED = "archived"
    ASSIGNED = "assigned"
    AUDITED = "audited"
    AUDITED_COMPLETED = "Audited Completed"
    AWAITING_APPROVAL = "Awaiting Approval"
    AWAITING_FEEDBACK = "Awaiting Feedback"
    AWAITING_PAYMENT = "Awaiting Payment"
    AWAITING_SUBMISSION = "awaiting_submission"
    AUTHORIZED = "Authorized"
    BACKED_UP = "Backed Up"
    BACKED_UP_COMPLETED = "Backed Up Completed"
    BLOCKED = "Blocked"
    CALIBRATED = "Calibrated"
    CANCELED = "canceled"
    CERTIFIED = "Certified"
    CLARIFICATION_PROVIDED = "Clarification Provided"
    COMMITTED = "Committed"
    CONFIRMED = "Confirmed"
    CONFIGURED = "Configured"
    CONFIGURED_COMPLETED = "Configured Completed"
    CONVERTED = "Converted"
    DEBUGGED = "Debugged"
    DEBUGGED_COMPLETED = "Debugged Completed"
    DEALLOCATED = "Deallocated"
    DEINSTALLED = "Deinstalled"
    DEINSTALLED_COMPLETED = "Deinstalled Completed"
    DEMO = "Demo"
    DENIED = "Denied"
    DEPLOYED = "Deployed"
    DEPLOID = "Deploid" # Added
    DISPATCHED = "Dispatched"
    DISPUTED = "Disputed"
    DISTRIBUTED = "Distributed"
    DOCUMENTED = "Documented"
    DOCUMENTED_COMPLETED = "Documented Completed"
    DOWNGRADED = "Downgraded"
    DOWNGRADED_COMPLETED = "Downgraded Completed"
    DRAFT = "draft"
    DRAFTING = "Drafting"
    ESCALATED = "Escalated"
    EXEMPT = "exempt"
    EXPORTED = "Exported"
    EXTENSION_GRANTED = "extension_granted"
    EXTENSION_REQUESTED = "extension_requested"
    EXTRA_CREDIT = "extra_credit"
    FEEDBACK_PROVIDED = "Feedback Provided"
    FINALIZED = "Finalized"
    FLAGGED = "Flagged"
    GRANTED = "Granted"
    GRADED = "graded"
    HIDDEN = "Hidden"
    IMPORTED = "Imported"
    IN_DISCUSSION = "In Discussion"
    IN_TESTING = "In Testing"
    INSPECTED = "Inspected"
    INSTALLED = "Installed"
    INSTALLED_COMPLETED = "Installed Completed"
    INTERNAL_REVIEW_COMPLETED = "Internal Review Completed"
    LATE_SUBMISSION = "late_submission"
    MAINTAINED = "Maintained"
    MAINTENANCE_COMPLETED = "Maintenance Completed"
    MARKED_AS_EXCUSED = "marked_as_excused"
    MARKED_AS_MISSING = "marked_as_missing"
    MARKED_FOR_REVIEW = "marked_for_review"
    MERGED = "Merged"
    MIGRATED = "Migrated"
    MONITORED = "Monitored"
    MONITORED_COMPLETED = "Monitored Completed"
    NEEDS_ACTION = "Needs Action"
    NEEDS_ANALYSIS = "Needs Analysis"
    NEEDS_APPROVAL = "Needs Approval" # Added
    NEEDS_AUDIT = "Needs Audit"
    NEEDS_BACKUP = "Needs Backup"
    NEEDS_CALIBRATION = "Needs Calibration"
    NEEDS_CERTIFICATION = "Needs Certification"
    NEEDS_CLARIFICATION = "Needs Clarification"
    NEEDS_CONFIGURATION = "Needs Configuration"
    NEEDS_DEBUGGING = "Needs Debugging"
    NEEDS_DEINSTALLATION = "Needs Deinstallation"
    NEEDS_DOCUMENTATION = "Needs Documentation"
    NEEDS_DOWNGRADE = "Needs Downgrade"
    NEEDS_EXTERNAL_REVIEW = "Needs External Review"
    NEEDS_GRADING = "needs_grading"
    NEEDS_INSPECTION = "Needs Inspection"
    NEEDS_INSTALLATION = "Needs Installation"
    NEEDS_INTERNAL_REVIEW = "Needs Internal Review"
    NEEDS_MAINTENANCE = "Needs Maintenance"
    NEEDS_MONITORING = "Needs Monitoring"
    NEEDS_OPTIMIZATION = "Needs Optimization"
    NEEDS_REPAIR = "Needs Repair"
    NEEDS_REPLACEMENT = "Needs Replacement"
    NEEDS_RESTORE = "Needs Restore"
    NEEDS_RESTART = "Needs Restart"
    NEEDS_REVIEW = "Needs Review"
    NEEDS_REVISION = "needs_revision"
    NEEDS_SCALING = "Needs Scaling"
    NEEDS_TESTING = "Needs Testing"
    NEEDS_UPDATE = "Needs Update"
    NEGOTIATION_COMPLETED = "Negotiation Completed"
    NOT_STARTED = "not_started"
    OPTIMIZED = "Optimized"
    OPTIMIZED_COMPLETED = "Optimized Completed"
    OVERDUE = "overdue"
    PAID = "Paid"
    PARTIALLY_GRADED = "partially_graded"
    PARTIALLY_PAID = "Partially Paid"
    PARTIALLY_REFUNDED = "Partially Refunded"
    PARTIALLY_SUBMITTED = "partially_submitted"
    PATCHED = "Patched"
    PLAGIARIZED = "plagiarized"
    POSTPONED = "Postponed"
    PREPARED = "Prepared"
    PRE_RELEASE = "Pre-Release"
    PREVIEW = "Preview"
    PROCESSING = "Processing"
    PROCESSING_PAYMENT = "Processing Payment"
    PROVISIONALLY_GRADED = "provisionally_graded"
    PUBLISHED = "Published"
    PURCHASED = "Purchased"
    REACTIVATED = "Reactivated"
    RECALCULATED = "recalculated"
    RECOUNTED = "recounted"
    REFACTORED = "Refactored"
    REFUNDED = "Refunded"
    REMEDIATION_COMPLETED = "remediation_completed"
    REMEDIATION_PENDING = "remediation_pending"
    REMEDIATION_REQUIRED = "remediation_required"
    REMOVED = "Removed"
    REOPENED = "reopened"
    REPAIRED = "Repaired"
    REPAIRED_COMPLETED = "Repaired Completed"
    REPLACED = "Replaced"
    REPLACED_COMPLETED = "Replaced Completed"
    REQUESTED = "Requested"
    REQUIRES_AUTHORIZATION = "Requires Authorization"
    REQUIRES_FEEDBACK = "Requires Feedback"
    REQUIRES_SIGNATURE = "Requires Signature"
    REQUIRES_VALIDATION = "Requires Validation"
    RESOLVED = "Resolved"
    RESTORED = "Restored"
    RESTORED_COMPLETED = "Restored Completed"
    RESTARTED = "Restarted"
    RESTARTED_COMPLETED = "Restarted Completed"
    REVIEWED = "Reviewed"
    REVISED = "Revised"
    REWRITTEN = "Rewritten"
    ROLLED_BACK = "Rolled Back"
    SAMPLE = "Sample"
    SCALED = "Scaled"
    SCALED_GRADE = "scaled_grade"
    SCALED_COMPLETED = "Scaled Completed"
    SCHEDULED_FOR_DELETION = "Scheduled for Deletion"
    SIGNED = "Signed"
    SPLIT = "Split"
    STARTED = "Started"
    STOPPED = "Stopped"
    SUBMITTED = "submitted"
    SUSPENDED = "Suspended"
    TEMPLATE = "Template"
    TENTATIVE = "Tentative"
    TESTED = "Tested"
    TESTING_COMPLETED = "Testing Completed"
    TRANSFERRED = "Transferred"
    UNDEPLOYED = "Undeployed"
    UNGRADED = "ungraded"
    UNCOMMITTED = "Uncommitted"
    UNPUBLISHED = "Unpublished"
    UNVERIFIED = "Unverified"
    UPDATED = "Updated"
    UPDATED_COMPLETED = "Updated Completed"
    UPGRADED = "Upgraded"
    UPGRADED_COMPLETED = "Upgraded Completed"
    VALIDATED = "Validated"
    VALIDATED_COMPLETED = "Validation Completed" # Added
    VALIDATING = "Validating"
    VERIFIED = "Verified"
    VISIBLE = "Visible"
    VOIDED = "voided"