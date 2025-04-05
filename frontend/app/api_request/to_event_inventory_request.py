#  frontend/app/to_event_functions_request.py

import requests
from typing import List, Dict
import logging
import tkinter as tk
import uuid
import re
from tkinter import messagebox
from datetime import datetime, timezone, date
from ..config import *

logger = logging.getLogger(__name__)

project_id = 'work_id'
# Create to-event inventry list request api
def create_to_event_inventory_list(item_data: dict):
    """Inventory item creation with all fields optional"""
    try:
        # Helper function to clean input values
        def clean_value(value):
            if value is None or str(value).strip() == '':
                return None
            return str(value).strip()
        
        # Helper function for numeric fields (as strings)
        def clean_number_str(value):
            try:
                if value is None or str(value).strip() == '':
                    return None
                # Convert to number first to validate, then back to string
                num = float(value) if '.' in str(value) else int(float(value))
                return str(num)
            except (ValueError, TypeError):
                return None

        def clean_date(date_str):
            try:
                if date_str:
                    return datetime.strptime(date_str, '%Y-%m-%d').date().isoformat()
                return None
            except (ValueError, TypeError):
                return None
        
        # Clean project ID
        project_id = clean_value(item_data.get('work_id'))
        if project_id:
            project_id = ''.join(c for c in project_id if c.isdigit())
        
        # Base payload with optional fields
        payload = {
            "project_id": clean_value(item_data.get('work_id')),
            "employee_name": clean_value(item_data.get('employee_name')),
            "location": clean_value(item_data.get('location')),
            "client_name": clean_value(item_data.get('client_name')),
            "setup_date": clean_date(item_data.get('setup_date')),
            "project_name": clean_value(item_data.get('project_name')),
            "event_date": clean_date(item_data.get('event_date')),
            "submitted_by": "inventory-admin",
            "inventory_items": []
        }

        # Process all inventory items from all rows
        for item in item_data.get('inventory_items', []):
            inventory_item = {
                "zone_active": clean_value(item.get('zone_active')),
                "sno": clean_value(item.get('sno')),
                "name": clean_value(item.get('name')),
                "description": clean_value(item.get('description')),
                "quantity": clean_number_str(item.get('quantity')),
                "material": clean_value(item.get('material')),
                "comments": clean_value(item.get('comments')),
                "total": clean_number_str(item.get('total')),
                "unit": clean_value(item.get('unit')),
                "per_unit_power": clean_number_str(item.get('per_unit_power')),
                "total_power": clean_number_str(item.get('total_power')),
                "status": clean_value(item.get('status')),
                "poc": clean_value(item.get('poc'))
            }
            # Only add if at least one field has value
            if any(v is not None for v in inventory_item.values()):
                payload["inventory_items"].append(
                    {k: v for k, v in inventory_item.items() if v is not None}
                )

        # Remove empty values from main payload
        payload = {k: v for k, v in payload.items() if v is not None and v != []}

        logger.debug(f"Sending payload: {payload}")

        # Use helper function for API request
        response = make_api_request(
            "POST",
            "to_event-create-item/",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        return response.json()
        
    except Exception as e:
        error_msg = f"Could not add inventory item: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

# Load submitted forms from from db the API
def load_submitted_project_from_db() -> List[Dict]:
    """Fetch submitted forms from the API"""
    try:
        response = make_api_request(
            "GET",
            "to_event-load-submitted-project-db/"
        )
        
        print(response.json())
        return [format_project_item(item) for item in response.json()]
        
    except Exception as e:
        error_msg = "Could not fetch submitted forms"
        logger.error(f"{error_msg}: {str(e)}")
        messagebox.showerror("Error", error_msg)
        return []

# Update data into existing record of ``work_id`` in the API
def update_submitted_project_in_db(work_id: str, data: dict) -> bool:
    """Update submitted forms in the API"""
    try:
        response = make_api_request(
            "PUT",  # Changed from POST to PUT for updates
            f"to_event-update-submitted-project-db/{work_id}",
            headers={"Content-Type": "application/json"},
            json=data
        )
        return True
        
    except Exception as e:
        error_msg = "Could not update submitted forms"
        logger.error(f"{error_msg}: {str(e)}")
        messagebox.showerror("Error", error_msg)
        return False

# Search for Project with there inventory list by [Project_id] by clicking search
def search_project_details_by_id(work_id: str) -> List[Dict]:
    """Fetch inventory data filtered by a single ID from the API"""
    try:
        if not work_id:
            raise ValueError("Project ID is required for searching")

        response = make_api_request(
            "GET",
            "search-to-event-inventory/",
            params={"project_id": work_id}
        )
        
        return [format_project_item(item) for item in response.json()]
        
    except ValueError as e:
        logger.error(f"Search validation error: {str(e)}")
        messagebox.showwarning("Search Error", str(e))
        return []
    except Exception as e:
        error_msg = "Could not fetch inventory data"
        logger.error(f"{error_msg}: {str(e)}")
        messagebox.showerror("Error", error_msg)
        return []


# Add new inventory items to the database with proper data formatting
def format_project_item(item: dict) -> dict:
    """Format project item from API response to frontend format"""
    # Handle both flat structure (old) and nested inventory_items (new)
    if 'inventory_items' not in item:
        # Convert flat structure to nested
        inventory_item = {
            'zone_active': item.get('zone_active'),
            'sno': item.get('sno'),
            'name': item.get('name'),
            'description': item.get('description'),
            'quantity': item.get('quantity'),
            'material': item.get('material'),
            'comments': item.get('comments'),
            'total': item.get('total'),
            'unit': item.get('unit'),
            'per_unit_power': item.get('per_unit_power'),
            'total_power': item.get('total_power'),
            'status': item.get('status'),
            'poc': item.get('poc')
        }
        inventory_items = [inventory_item]
    else:
        inventory_items = item.get('inventory_items', [])
    
    return {
        'work_id': item.get('project_id'),
        'employee_name': item.get('employee_name'),
        'location': item.get('location'),
        'client_name': item.get('client_name'),
        'setup_date': item.get('setup_date'),
        'project_name': item.get('project_name'),
        'event_date': item.get('event_date'),
        'inventory_items': inventory_items
    }