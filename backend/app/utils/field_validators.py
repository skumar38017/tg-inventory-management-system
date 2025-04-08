
# backend/app/schema/field_validators.py
import re
from datetime import datetime, date
from typing import Optional
from pydantic import ValidationError


def format_project_id(v: Optional[str]) -> str:
    """
    Validates and formats project_id to include the 'PRJ' prefix.
    Removes any non-numeric characters after 'PRJ'.
    """
    if v is None:
        raise ValueError("Project_id cannot be empty")
    clean_id = re.sub(r'^PRJ', '', str(v))
    if not clean_id.isdigit():
        raise ValueError("Project_id must contain only numbers after prefix")
    return f"PRJ{clean_id}"


def parse_date_field(v: Optional[str]) -> Optional[date]:
    """
    Tries to parse a string into a date object. Supports both ISO and custom formats.
    """
    if isinstance(v, str):
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            try:
                return datetime.fromisoformat(v).date()
            except ValueError:
                return None
    elif isinstance(v, datetime):
        return v.date()
    return v


def convert_empty_string_to_none(v: Optional[str]) -> Optional[str]:
    """
    Converts empty strings to None.
    """
    return None if v == '' else v


def convert_unit_to_string(v: Optional[str]) -> Optional[str]:
    """
    Converts non-string values of 'unit' to string.
    """
    if v is None:
        return None
    return str(v) if not isinstance(v, str) else v


def convert_numbers_to_strings(v: Optional[str]) -> Optional[str]:
    """
    Converts non-string numeric values (float, int) to strings.
    """
    if v is None:
        return None
    return str(v) if not isinstance(v, str) else v


def handle_created_at_typo(v, values):
    """
    Fixes 'cretaed_at' typo to 'created_at'.
    """
    if v is None and 'cretaed_at' in values.data:
        return values.data['cretaed_at']
    return v
