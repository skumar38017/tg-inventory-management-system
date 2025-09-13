# backend/app/utils/date_utils.py
from datetime import datetime, date, timezone
from typing import Union, Optional

UTC_TIMEZONE = timezone.utc

class UTCDateUtils:
    """Utility class for handling dates in UTC timezone"""
    
    @staticmethod
    def get_current_datetime() -> datetime:
        """Get current datetime in UTC timezone as datetime object"""
        return datetime.now(UTC_TIMEZONE)
    
    @staticmethod
    def get_current_datetime_str() -> str:
        """Get current datetime in UTC timezone as formatted string (YYYY-MM-DD HH:MM:SS)"""
        return datetime.now(UTC_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_current_datetime_iso() -> str:
        """Get current datetime in UTC timezone as ISO format string"""
        return datetime.now(UTC_TIMEZONE).isoformat()
    
    @staticmethod
    def get_current_date() -> date:
        """Get current date in UTC timezone"""
        return datetime.now(UTC_TIMEZONE).date()
    
    @staticmethod
    def format_date(dt: Union[date, datetime, None]) -> Optional[str]:
        """Format date/datetime to YYYY-MM-DD string"""
        if dt is None:
            return None
        if isinstance(dt, datetime):
            return dt.date().isoformat()
        return dt.isoformat()
    
    @staticmethod
    def format_datetime(dt: Union[datetime, None]) -> Optional[str]:
        """Format datetime to ISO string with UTC timezone"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC_TIMEZONE)
        else:
            dt = dt.astimezone(UTC_TIMEZONE)
        return dt.isoformat()
    
    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[date]:
        """Parse date string in YYYY-MM-DD format to date object"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    
    @staticmethod
    def parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string to datetime object with UTC timezone"""
        if not datetime_str:
            return None
        try:
            dt = datetime.fromisoformat(datetime_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC_TIMEZONE)
            else:
                dt = dt.astimezone(UTC_TIMEZONE)
            return dt
        except ValueError:
            return None
    
    @staticmethod
    def validate_date_field(value: Union[str, date, datetime, None]) -> Optional[date]:
        """Pydantic validator for date fields"""
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return UTCDateUtils.parse_date(value)
        return None
    
    @staticmethod
    def validate_datetime_field(value: Union[str, datetime, None]) -> Optional[datetime]:
        """Pydantic validator for datetime fields"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return UTCDateUtils.parse_datetime(value)
        return None
    
