# backend/app/utils/field_validators.py
import re
from datetime import datetime, date, timezone
from typing import Optional, Union, Dict, Any, Tuple
from enum import Enum
from pydantic import field_validator, model_validator, validator, ValidationInfo

# ---------------------------- Common Enums ----------------------------
class StatusEnum(str, Enum):
    ACTIVE = "Active"
    ADJUSTED = "adjusted"
    ALLOCATED = "Allocated"
    ANALYZED = "Analyzed"
    ANALYZED_COMPLETED = "Analyzed Completed"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_REJECTED = "appeal_rejected"
    APPROVED = "Approved"
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
    CANCELLED = "Cancelled"
    CANCELED = "canceled"
    CERTIFIED = "Certified"
    CLARIFICATION_PROVIDED = "Clarification Provided"
    CLOSED = "Closed"
    COMMITTED = "Committed"
    COMPLETED = "completed"
    CONFIRMED = "Confirmed"
    CONFIGURED = "Configured"
    CONFIGURED_COMPLETED = "Configured Completed"
    CONVERTED = "Converted"
    DEBUGGED = "Debugged"
    DEBUGGED_COMPLETED = "Debugged Completed"
    DEALLOCATED = "Deallocated"
    DEINSTALLED = "Deinstalled"
    DEINSTALLED_COMPLETED = "Deinstalled Completed"
    DELAYED = "Delayed"
    DELIVERED = "Delivered"
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
    EXPIRED = "Expired"
    EXPORTED = "Exported"
    EXTENSION_GRANTED = "extension_granted"
    EXTENSION_REQUESTED = "extension_requested"
    EXTRA_CREDIT = "extra_credit"
    FAILED = "Failed"
    FEEDBACK_PROVIDED = "Feedback Provided"
    FINALIZED = "Finalized"
    FLAGGED = "Flagged"
    GRANTED = "Granted"
    GRADED = "graded"
    HIDDEN = "Hidden"
    IMPORTED = "Imported"
    IN_DISCUSSION = "In Discussion"
    IN_PROGRESS = "In Progress" # Added
    IN_TESTING = "In Testing"
    IN_TRANSIT = "In Transit"
    INACTIVE = "Inactive"
    INHOUSE = "In House"
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
    ON_HOLD = "On Hold"
    OPEN = "Open"
    OPTIMIZED = "Optimized"
    OPTIMIZED_COMPLETED = "Optimized Completed"
    OUTSIDE = "Outside"
    OVERDUE = "overdue"
    PAID = "Paid"
    PARTIALLY_GRADED = "partially_graded"
    PARTIALLY_PAID = "Partially Paid"
    PARTIALLY_REFUNDED = "Partially Refunded"
    PARTIALLY_SUBMITTED = "partially_submitted"
    PATCHED = "Patched"
    PENDING = "Pending"
    PENDING_REVIEW = "pending_review"
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
    REJECTED = "rejected"
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
    RESERVED = "Reserved"
    RESCHEDULED = "Rescheduled"
    RESOLVED = "Resolved"
    RESTORED = "Restored"
    RESTORED_COMPLETED = "Restored Completed"
    RESTARTED = "Restarted"
    RESTARTED_COMPLETED = "Restarted Completed"
    RETURN = "Returned"
    REVIEWED = "Reviewed"
    REVISED = "Revised"
    REWRITTEN = "Rewritten"
    ROLLED_BACK = "Rolled Back"
    SAMPLE = "Sample"
    SCALED = "Scaled"
    SCALED_GRADE = "scaled_grade"
    SCALED_COMPLETED = "Scaled Completed"
    SCHEDULED = "Scheduled"
    SCHEDULED_FOR_DELETION = "Scheduled for Deletion"
    SHIPPED = "Shipped"
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
    UNDER_APPEAL = "under_appeal"
    UNDER_DEVELOPMENT = "Under Development"
    UNDER_NEGOTIATION = "Under Negotiation"
    UNDER_REVIEW = "Under Review"
    UNAUTHORIZED = "Unauthorized"
    UNCONFIGURED = "Unconfigured"
    UNDEPLOYED = "Undeployed" # Added again to ensure no accidental removal
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
    WAITLISTED = "Waitlisted"
    WITHDRAWN = "Withdrawn"
# ---------------------------- Shared Validators ----------------------------
class BaseValidators:
    """Contains validators that can be reused across different schemas"""
    
    @staticmethod
    def format_id_field(v: Optional[str], prefix: str) -> Optional[str]:
        """Generic ID formatter that adds prefix if missing"""
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        if not v.startswith(prefix):
            return f"{prefix}{v}"
        return v

    @staticmethod
    def validate_date_field(v) -> Optional[date]:
        """Parse date from string or datetime object"""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                try:
                    return datetime.fromisoformat(v).date()
                except ValueError:
                    raise ValueError("Date must be in YYYY-MM-DD format")
        elif isinstance(v, datetime):
            return v.date()
        return v

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
    def empty_string_to_none(v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None"""
        return None if v == '' else v

    @staticmethod
    def convert_to_string(v) -> Optional[str]:
        """Convert value to string if it isn't already"""
        if v is None:
            return None
        return str(v) if not isinstance(v, str) else v

    @staticmethod
    def handle_created_at_typo(v, values: Dict) -> datetime:
        """Handle common 'cretaed_at' typo in timestamp fields"""
        if v is None and 'cretaed_at' in values:
            return values['cretaed_at']
        return v or datetime.now(timezone.utc)

# ---------------------------- Schema-Specific Validators ----------------------------
class AssignmentInventoryValidations(BaseValidators):
    """Validators specific to assignment inventory"""
    
    @field_validator('inventory_id', mode='before')
    def validate_inventory_id(cls, v):
        return cls.format_id_field(v, 'INV')

    @field_validator('project_id', mode='before')
    def validate_project_id(cls, v):
        return cls.format_id_field(v, 'PRJ')

    @field_validator('product_id', mode='before')
    def validate_product_id(cls, v):
        return cls.format_id_field(v, 'PRD')

    @field_validator('assigned_date', 'assignment_return_date', mode='before')
    def validate_assignment_dates(cls, v):
        return cls.validate_date_field(v)

class EntryInventoryValidations(BaseValidators):
    """Validators specific to entry inventory"""
    
    @field_validator('product_id', mode='before')
    def validate_product_id(cls, v):
        if v is None:
            raise ValueError("Product ID cannot be empty")
        clean_id = re.sub(r'^PRD', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Product ID must contain only numbers after prefix")
        return f"PRD{clean_id}"

    @field_validator('inventory_id', mode='before')
    def validate_inventory_id(cls, v):
        if v is None:
            raise ValueError("Inventory ID cannot be empty")
        clean_id = re.sub(r'^INV', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Inventory ID must contain only numbers after prefix")
        return f"INV{clean_id}"
    
    @validator('on_rent', 'rented_inventory_returned', 'on_event', 'in_office', 'in_warehouse', pre=True)
    def validate_boolean_fields(cls, v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return v.lower()
        return "false"

    @field_validator('barcode_image_url', mode='before')
    def clean_barcode_url(cls, v):
        return cls.empty_string_to_none(v.replace('\"', ''))

class ToEventInventoryValidations(BaseValidators):
    """Validators specific to event inventory"""
    
    @field_validator('project_id', mode='before')
    def validate_project_id(cls, v):
        if v is None:
            raise ValueError("Project_id cannot be empty")
        clean_id = re.sub(r'^PRJ', '', str(v))
        if not clean_id.isdigit():
            raise ValueError("Project_id must contain only numbers after prefix")
        return f"PRJ{clean_id}"

    @model_validator(mode='before')
    def handle_event_timestamps(cls, values: Dict) -> Dict:
        """Special handling for event timestamps including typo correction"""
        if not isinstance(values, dict):
            return values
            
        values['created_at'] = cls.handle_created_at_typo(
            values.get('created_at'), 
            values
        )
        values['updated_at'] = datetime.now(timezone.utc)
            
        return values

class WastageInventoryValidations(BaseValidators):
    """Validators specific to wastage inventory"""
    
    @field_validator('inventory_id', mode='before')
    def validate_inventory_id(cls, v):
        return cls.format_id_field(v, 'INV')

    @field_validator('project_id', mode='before')
    def validate_project_id(cls, v):
        return cls.format_id_field(v, 'PRJ')

    @field_validator('product_id', mode='before')
    def validate_product_id(cls, v):
        return cls.format_id_field(v, 'PRD')

    @field_validator('quantity', mode='before')
    def validate_wastage_quantity(cls, v):
        """Special quantity validator for wastage that requires whole numbers"""
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

    @field_validator('receive_date', 'event_date', 'wastage_date', mode='before')
    def validate_wastage_dates(cls, v):
        return cls.validate_date_field(v)
    

# from .validations.inventory_validations import (
#     AssignmentInventoryValidations,
#     EntryInventoryValidations,
#     ToEventInventoryValidations,
#     WastageInventoryValidations,
#     AssignmentStatusEnum,
#     EventStatusEnum
# )