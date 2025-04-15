# backend/app/utils/field_validators.py
import re
from datetime import datetime, date, timezone
from typing import Optional, Union, Dict, Any, Tuple
from enum import Enum
from pydantic import field_validator, model_validator, validator, ValidationInfo

# ---------------------------- Common Enums ----------------------------
class StatusEnum(str, Enum):
    ASSIGNED = "assigned"
    SUBMITTED = "submitted"
    GRADED = "graded"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"
    DRAFT = "draft"
    OVERDUE = "overdue"
    EXEMPT = "exempt"
    RESUBMITTED = "resubmitted"
    NOT_STARTED = "not_started"
    COMPLETED = "completed"
    CANCELED = "canceled"
    PARTIALLY_GRADED = "partially_graded"
    MARKED_FOR_REVIEW = "marked_for_review"
    REOPENED = "reopened"
    ARCHIVED = "archived"
    NEEDS_GRADING = "needs_grading"
    NEEDS_REVISION = "needs_revision"
    AWAITING_SUBMISSION = "awaiting_submission"
    EXTENSION_GRANTED = "extension_granted"
    EXTENSION_REQUESTED = "extension_requested"
    LATE_SUBMISSION = "late_submission"
    PLAGIARIZED = "plagiarized"
    MARKED_AS_MISSING = "marked_as_missing"
    MARKED_AS_EXCUSED = "marked_as_excused"
    UNDER_APPEAL = "under_appeal"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_REJECTED = "appeal_rejected"
    REMEDIATION_REQUIRED = "remediation_required"
    REMEDIATION_COMPLETED = "remediation_completed"
    REMEDIATION_PENDING = "remediation_pending"
    VOIDED = "voided"
    RECALCULATED = "recalculated"
    PARTIALLY_SUBMITTED = "partially_submitted"
    SCALED_GRADE = "scaled_grade"
    EXTRA_CREDIT = "extra_credit"
    AUDITED = "audited"
    PROVISIONALLY_GRADED = "provisionally_graded"
    RECOUNTED = "recounted"
    UNGRADED = "ungraded"
    ADJUSTED = "adjusted"
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    INHOUSE = "In House"
    OUTSIDE = "Outside"
    PURCHASED = "Purchased"
    RETURN = "Returned"
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
    POSTPONED = "Postponed"
    CONFIRMED = "Confirmed"
    TENTATIVE = "Tentative"
    RESCHEDULED = "Rescheduled"
    BLOCKED = "Blocked"
    VALIDATED = "Validated"
    PROCESSING = "Processing"
    DISPATCHED = "Dispatched"
    AWAITING_PAYMENT = "Awaiting Payment"
    PAID = "Paid"
    REFUNDED = "Refunded"
    PARTIALLY_REFUNDED = "Partially Refunded"
    PARTIALLY_PAID = "Partially Paid"
    DISPUTED = "Disputed"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"
    FLAGGED = "Flagged"
    REVISED = "Revised"
    UPDATED = "Updated"
    PUBLISHED = "Published"
    UNPUBLISHED = "Unpublished"
    HIDDEN = "Hidden"
    VISIBLE = "Visible"
    SUSPENDED = "Suspended"
    REACTIVATED = "Reactivated"
    REMOVED = "Removed"
    IMPORTED = "Imported"
    EXPORTED = "Exported"
    MERGED = "Merged"
    SPLIT = "Split"
    CONVERTED = "Converted"
    TRANSFERRED = "Transferred"
    ALLOCATED = "Allocated"
    DEALLOCATED = "Deallocated"
    COMMITTED = "Committed"
    UNCOMMITTED = "Uncommitted"
    REQUESTED = "Requested"
    GRANTED = "Granted"
    DENIED = "Denied"
    AUTHORIZED = "Authorized"
    UNAUTHORIZED = "Unauthorized"
    VERIFIED = "Verified"
    UNVERIFIED = "Unverified"
    PREPARED = "Prepared"
    DISTRIBUTED = "Distributed"
    INSTALLED = "Installed"
    DEINSTALLED = "Deinstalled"
    DEPLOYED = "Deployed"
    UNDEPLOYED = "Undeployed"
    CONFIGURED = "Configured"
    UNCONFIGURED = "Unconfigured"
    UPGRADED = "Upgraded"
    DOWNGRADED = "Downgraded"
    RESTARTED = "Restarted"
    STOPPED = "Stopped"
    STARTED = "Started"
    REPLACED = "Replaced"
    REPAIRED = "Repaired"
    MAINTAINED = "Maintained"
    BACKED_UP = "Backed Up"
    RESTORED = "Restored"
    TESTED = "Tested"
    DEBUGGED = "Debugged"
    OPTIMIZED = "Optimized"
    SCALED = "Scaled"
    MONITORED = "Monitored"
    ANALYZED = "Analyzed"
    DOCUMENTED = "Documented"
    REVIEWED = "Reviewed"
    VALIDATING = "Validating"
    PROCESSING_PAYMENT = "Processing Payment"
    AWAITING_APPROVAL = "Awaiting Approval"
    NEEDS_REVIEW = "Needs Review"
    NEEDS_ACTION = "Needs Action"
    IN_DISCUSSION = "In Discussion"
    UNDER_DEVELOPMENT = "Under Development"
    IN_TESTING = "In Testing"
    READY_FOR_RELEASE = "Ready for Release"
    RELEASED = "Released"
    ROLLED_BACK = "Rolled Back"
    DEMO = "Demo"
    SAMPLE = "Sample"
    TEMPLATE = "Template"
    DRAFTING = "Drafting"
    FINALIZED = "Finalized"
    PREVIEW = "Preview"
    PRE_RELEASE = "Pre-Release"
    PATCHED = "Patched"
    MIGRATED = "Migrated"
    REFACTORED = "Refactored"
    REWRITTEN = "Rewritten"
    SCHEDULED_FOR_DELETION = "Scheduled for Deletion"
    NEEDS_ATTENTION = "Needs Attention"
    REQUIRES_FEEDBACK = "Requires Feedback"
    AWAITING_FEEDBACK = "Awaiting Feedback"
    FEEDBACK_PROVIDED = "Feedback Provided"
    UNDER_NEGOTIATION = "Under Negotiation"
    NEGOTIATION_COMPLETED = "Negotiation Completed"
    NEEDS_CLARIFICATION = "Needs Clarification"
    CLARIFICATION_PROVIDED = "Clarification Provided"
    REQUIRES_SIGNATURE = "Requires Signature"
    SIGNED = "Signed"
    NEEDS_APPROVAL_FROM_HIGHER_AUTHORITY = "Needs Approval From Higher Authority"
    APPROVED_BY_HIGHER_AUTHORITY = "Approved By Higher Authority"
    NEEDS_INTERNAL_REVIEW = "Needs Internal Review"
    INTERNAL_REVIEW_COMPLETED = "Internal Review Completed"
    NEEDS_EXTERNAL_REVIEW = "Needs External Review"
    EXTERNAL_REVIEW_COMPLETED = "External Review Completed"
    REQUIRES_VALIDATION = "Requires Validation"
    VALIDATION_COMPLETED = "Validation Completed"
    REQUIRES_AUTHORIZATION = "Requires Authorization"
    AUTHORIZATION_COMPLETED = "Authorization Completed"
    NEEDS_CERTIFICATION = "Needs Certification"
    CERTIFIED = "Certified"
    NEEDS_AUDIT = "Needs Audit"
    AUDITED_COMPLETED = "Audited Completed"
    NEEDS_INSPECTION = "Needs Inspection"
    INSPECTED = "Inspected"
    NEEDS_CALIBRATION = "Needs Calibration"
    CALIBRATED = "Calibrated"
    NEEDS_TESTING = "Needs Testing"
    TESTING_COMPLETED = "Testing Completed"
    NEEDS_REPAIR = "Needs Repair"
    REPAIRED_COMPLETED = "Repaired Completed"
    NEEDS_MAINTENANCE = "Needs Maintenance"
    MAINTENANCE_COMPLETED = "Maintenance Completed"
    NEEDS_UPDATE = "Needs Update"
    UPDATED_COMPLETED = "Updated Completed"
    NEEDS_INSTALLATION = "Needs Installation"
    INSTALLED_COMPLETED = "Installed Completed"
    NEEDS_DEINSTALLATION = "Needs Deinstallation"
    DEINSTALLED_COMPLETED = "Deinstalled Completed"
    NEEDS_CONFIGURATION = "Needs Configuration"
    CONFIGURED_COMPLETED = "Configured Completed"
    NEEDS_UPGRADE = "Needs Upgrade"
    UPGRADED_COMPLETED = "Upgraded Completed"
    NEEDS_DOWNGRADE = "Needs Downgrade"
    DOWNGRADED_COMPLETED = "Downgraded Completed"
    NEEDS_RESTART = "Needs Restart"
    RESTARTED_COMPLETED = "Restarted Completed"
    NEEDS_REPLACEMENT = "Needs Replacement"
    REPLACED_COMPLETED = "Replaced Completed"
    NEEDS_BACKUP = "Needs Backup"
    BACKED_UP_COMPLETED = "Backed Up Completed"
    NEEDS_RESTORE = "Needs Restore"
    RESTORED_COMPLETED = "Restored Completed"
    NEEDS_DEBUGGING = "Needs Debugging"
    DEBUGGED_COMPLETED = "Debugged Completed"
    NEEDS_OPTIMIZATION = "Needs Optimization"
    OPTIMIZED_COMPLETED = "Optimized Completed"
    NEEDS_SCALING = "Needs Scaling"
    SCALED_COMPLETED = "Scaled Completed"
    NEEDS_MONITORING = "Needs Monitoring"
    MONITORED_COMPLETED = "Monitored Completed"
    NEEDS_ANALYSIS = "Needs Analysis"
    ANALYZED_COMPLETED = "Analyzed Completed"
    NEEDS_DOCUMENTATION = "Needs Documentation"
    DOCUMENTED_COMPLETED = "Documented Completed"

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