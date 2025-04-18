# backend/app/utils/date_utils.py
from datetime import datetime, date, timezone, timedelta
from typing import Optional, Union
from pydantic import field_validator

INDIAN_TIMEZONE = timezone(timedelta(hours=5, minutes=30))

class IndianDateUtils:
    """
    Utility class for handling dates in Indian timezone (IST)
    """
    
    @staticmethod
    def get_current_datetime() -> datetime:
        """Get current datetime in Indian timezone"""
        return datetime.now(INDIAN_TIMEZONE)
    
    @staticmethod
    def get_current_date() -> date:
        """Get current date in Indian timezone"""
        return IndianDateUtils.get_current_datetime().date()
    
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
        """Format datetime to ISO string with Indian timezone"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            # If no timezone info, assume it's in Indian timezone
            dt = dt.replace(tzinfo=INDIAN_TIMEZONE)
        else:
            # Convert to Indian timezone if it's in another timezone
            dt = dt.astimezone(INDIAN_TIMEZONE)
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
        """Parse ISO datetime string to datetime object with Indian timezone"""
        if not datetime_str:
            return None
        try:
            dt = datetime.fromisoformat(datetime_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=INDIAN_TIMEZONE)
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
            parsed = IndianDateUtils.parse_date(value)
            if parsed is None:
                raise ValueError("Date must be in YYYY-MM-DD format")
            return parsed
        raise ValueError("Invalid date format")
    
    @staticmethod
    def validate_datetime_field(value: Union[str, datetime, None]) -> Optional[datetime]:
        """Pydantic validator for datetime fields"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=INDIAN_TIMEZONE)
        if isinstance(value, str):
            parsed = IndianDateUtils.parse_datetime(value)
            if parsed is None:
                raise ValueError("Datetime must be in ISO format")
            return parsed
        raise ValueError("Invalid datetime format")