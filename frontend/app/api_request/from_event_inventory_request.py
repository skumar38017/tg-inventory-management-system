#  frontend/app/to_event_functions_request.py

import requests
from typing import List, Dict
import logging
import tkinter as tk
import uuid
import re
from tkinter import messagebox
from datetime import datetime, timezone, date
from config import *
from typing import Optional, Union


logger = logging.getLogger(__name__)

# Search for Project with there inventory list by [Project_id] by clicking search
DEFAULT_SUBMITTED_BY = "inventory-admin"

def search_return_details_by_id(work_id: str) -> List[Dict]:
    """Fetch inventory data filtered by a single work_id from the API"""
    if not work_id or not str(work_id).strip():
        print("Empty work_id provided for search {}".format(work_id))
        logger.error("Empty work_id provided for search")
        messagebox.showwarning("Search war", "Project ID is required for searching")
        return []
    
    try:
        # Ensure work_id has proper PRJ prefix if missing
        if not work_id.startswith('PRJ'):
            work_id = f'PRJ{work_id}'
            
        response = make_api_request(
            "GET",
            f"from_event-search-entries-by-project-id/{work_id}/"
        )
        
        if response.status_code == 404:
            return []  # Project not found is not an error case
            
        response.raise_for_status()
        
        # Debugging: Log the raw response
        logger.debug(f"Raw API response: {response.text}")
        
        # Handle response format
        data = response.json()
        
        # Case 1: Response is a single project object
        if isinstance(data, dict):
            return [format_return_project_item(data)]
            
        # Case 2: Response is a list of projects
        elif isinstance(data, list):
            return [format_return_project_item(item) for item in data]
            
        # Unexpected format
        else:
            logger.error(f"Unexpected API response format: {type(data)}")
            return []
            
    except Exception as e:
        warning_mess = f"New Entry is processing want to create a new entry: {str(e)}"
        logger.warning(warning_mess)
        messagebox.showerror("Error", warning_mess)
        return []

def clean_value(value: Optional[Union[str, int, float]]) -> Optional[str]:
    """Clean and validate input values"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return str(value)
    value = str(value).strip()
    return value if value else None

def clean_number(value: Optional[Union[str, int, float]]) -> Optional[Union[int, float]]:
    """Clean and validate numeric values"""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return value
        value = str(value).strip()
        if not value:
            return None
        return float(value) if '.' in value else int(float(value))
    except (ValueError, TypeError):
        return None

def clean_date(date_str: Optional[Union[str, date, datetime]]) -> Optional[str]:
    """Clean and validate date values"""
    if not date_str:
        return None
    try:
        if isinstance(date_str, (date, datetime)):
            return date_str.isoformat()
        return datetime.strptime(str(date_str), '%Y-%m-%d').date().isoformat()
    except (ValueError, TypeError):
        return None

# Create to-event inventory list request api
def create_to_return_inventory_list(item_data: dict):
    """Inventory item creation with proper validation and error handling for multiple items"""
    try:
        # Get and validate project_id
        project_id = clean_value(item_data.get('work_id')) or clean_value(item_data.get('project_id'))
        if not project_id:
            raise ValueError("Project ID is required")

        # Validate required fields
        required_fields = ['employee_name', 'location', 'client_name', 'project_name']
        for field in required_fields:
            if not clean_value(item_data.get(field)):
                raise ValueError(f"Field '{field}' is required")

        # Get and validate inventory items
        inventory_items = item_data.get('inventory_items', [])
        if not inventory_items:
            raise ValueError("At least one inventory item is required")

        # Prepare the main payload with common fields
        payload = {
            "project_id": project_id,
            "employee_name": clean_value(item_data.get('employee_name')),
            "location": clean_value(item_data.get('location')),
            "client_name": clean_value(item_data.get('client_name')),
            "setup_date": clean_date(item_data.get('setup_date')),
            "project_name": clean_value(item_data.get('project_name')),
            "event_date": clean_date(item_data.get('event_date')),
            "submitted_by": DEFAULT_SUBMITTED_BY,
            "inventory_items": []
        }

        # Prepare each inventory item with project_id included
        for inventory_item in inventory_items:
            # Validate required inventory fields
            inv_required_fields = ['name', 'quantity', 'unit']
            for field in inv_required_fields:
                if not clean_value(inventory_item.get(field)):
                    raise ValueError(f"Inventory field '{field}' is required")

            # Create item payload with project_id included
            item_payload = {
                "project_id": project_id, 
                "zone_active": clean_value(inventory_item.get('zone_active')),
                "sno": clean_value(inventory_item.get('sno')),
                "name": clean_value(inventory_item.get('name')),
                "description": clean_value(inventory_item.get('description')),
                "quantity": clean_number(inventory_item.get('quantity')),
                "comments": clean_value(inventory_item.get('comments')),
                "total": clean_number(inventory_item.get('total')),
                "unit": clean_value(inventory_item.get('unit')),
                "per_unit_power": clean_number(inventory_item.get('per_unit_power')),
                "total_power": clean_number(inventory_item.get('total_power')),
                "status": clean_value(inventory_item.get('status')),
                "poc": clean_value(inventory_item.get('poc')),
                "RecQty": clean_value(inventory_item.get('RecQty', "")),
            }

            # Remove None values except for project_id which is required
            item_payload = {k: v for k, v in item_payload.items() if v is not None}
            payload['inventory_items'].append(item_payload)

        logger.debug(f"Sending payload: {payload}")

        # Make single API call with all inventory items
        response = make_api_request(
            "POST",
            "from_event-create-item/",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        # Handle 422 validation errors with detailed messages
        if response.status_code == 422:
            try:
                errors = response.json().get('detail', [])
                error_msgs = []
                for error in errors:
                    loc = error.get('loc', [])
                    msg = error.get('msg', 'Validation error')
                    field = loc[-1] if loc else 'unknown field'
                    error_msgs.append(f"{field}: {msg}")
                raise ValueError("\n".join(error_msgs))
            except Exception as e:
                raise ValueError(f"Validation failed: {str(e)}")
        
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        error_msg = f"Could not add inventory items: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
            
# Load submitted forms from from db the API
def load_submitted_project_return_from_db() -> List[Dict]:
    """Fetch submitted forms from the API and return sorted by updated_at"""
    try:
        response = make_api_request(
            "GET",
            "from_event-load-project-redis/"
        )
        response = make_api_request(
            "GET",
            "to_event-load-submitted-project-redis/"
        )
        
        # Ensure we have a valid response
        if response.status_code != 200:
            logger.error(f"API returned status code: {response.status_code}")
            return []
            
        projects = response.json()
        
        # Validate we got a list of projects
        if not isinstance(projects, list):
            logger.error(f"Unexpected API response format: {projects}")
            return []
            
        # Format each project and sort by updated_at (newest first)
        formatted_projects = []
        for item in projects:
            try:
                formatted = format_return_project_item(item)
                # Ensure updated_at exists (set to empty string if missing)
                formatted['updated_at'] = item.get('updated_at', '')
                formatted_projects.append(formatted)
            except Exception as e:
                logger.error(f"Error formatting project item: {str(e)}")
                continue
                
        # Sort by updated_at in descending order (newest first)
        formatted_projects.sort(
            key=lambda x: x.get('updated_at', ''),
            reverse=True
        )
        
        return formatted_projects
        
    except Exception as e:
        error_msg = "Could not fetch submitted forms"
        logger.error(f"{error_msg}: {str(e)}")
        messagebox.showerror("Error", error_msg)
        return []

# Update data into existing record of ``work_id`` in the API
def update_submitted__return_project_in_db(work_id: str, data: dict) -> bool:
    """Update submitted forms in Redis via API"""
    try:
        # Prepare complete update payload with proper structure
        update_payload = {
            "project_id": work_id,  # Ensure project_id is included
            "employee_name": data.get('employee_name', ''),
            "location": data.get('location', ''),
            "client_name": data.get('client_name', ''),
            "setup_date": data.get('setup_date', ''),
            "project_name": data.get('project_name', ''),
            "event_date": data.get('event_date', ''),
            "inventory_items": []
        }
        
        # Process all inventory items with proper data types
        for item in data.get('inventory_items', []):
            inventory_item = {
                "project_id": work_id,  # Associate each item with project
                "zone_active": str(item.get('zone_active', '')),
                "sno": str(item.get('sno', '')),
                "name": str(item.get('name', '')),
                "description": str(item.get('description', '')),
                "quantity": str(item.get('quantity', '0')),
                "RecQty": str(item.get('RecQty', '')),
                "comments": str(item.get('comments', '')),
                "total": str(item.get('total', '0')),
                "unit": str(item.get('unit', 'pcs')),
                "per_unit_power": str(item.get('per_unit_power', '0')),
                "total_power": str(item.get('total_power', '0')),
                "status": str(item.get('status', 'active')),
                "poc": str(item.get('poc', ''))
            }
            update_payload['inventory_items'].append(inventory_item)
        
        logger.debug(f"Sending update payload: {update_payload}")
        
        response = make_api_request(
            "PUT",
            f"from_event-update-submitted-project-db/{work_id}/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json=update_payload,
            timeout=30  # Increased timeout for large payloads
        )
        
        if response.status_code != 200:
            logger.error(f"Update failed with status {response.status_code}. Response: {response.text}")
            return False
            
        # Verify the response contains the updated data
        response_data = response.json()
        if not response_data.get('success', False):
            logger.error(f"API reported failure: {response_data}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Update error: {str(e)}", exc_info=True)
        return False

# Add new inventory items to the database with proper data formatting
def format_return_project_item(item: dict) -> dict:
    """Format project item from API response to frontend format"""
    # Handle both flat structure (old) and nested inventory_items (new)
    if not isinstance(item, dict):
        logger.error(f"Invalid item format: {type(item)}")
        return {}
        
    if 'inventory_items' not in item:
        # Convert flat structure to nested
        inventory_item = {
            'project_id': item.get('work_id') or item.get('project_id'),
            'zone_active': item.get('zone_active'),
            'sno': item.get('sno'),
            'name': item.get('name'),
            'description': item.get('description'),
            'quantity': item.get('quantity'),
            'RecQty': item.get('RecQty'),
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
        'id': item.get('id'),
        'work_id': item.get('project_id') or item.get('work_id'),
        'employee_name': item.get('employee_name'),
        'location': item.get('location'),
        'client_name': item.get('client_name'),
        'setup_date': item.get('setup_date'),
        'project_name': item.get('project_name'),
        'event_date': item.get('event_date'),
        'inventory_items': inventory_items,
        'submitted_by': item.get('submitted_by'),
        'barcode': item.get('project_barcode')
    }