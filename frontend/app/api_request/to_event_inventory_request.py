#  frontend/app/to_event_functions_request.py

import requests
from typing import List, Dict
import logging
import tkinter as tk
import uuid
import re
from tkinter import messagebox
from datetime import datetime, timezone, date

logger = logging.getLogger(__name__)


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
                # Helper function for date fields

        def clean_date(date_str):
            try:
                if date_str:
                    return datetime.strptime(date_str, '%Y-%m-%d').date().isoformat()
                return None
            except (ValueError, TypeError):
                return None
        
        # Clean IDs - remove non-numeric characters but keep as strings
        project_id = clean_value(item_data.get('WorkID'))
        if project_id:
            project_id = ''.join(c for c in project_id if c.isdigit())
        
        # Payload construction - all fields optional
        payload = {
            # Basic information
            "project_id": project_id,
            "employee_name": clean_value(item_data.get('Employee')),
            "location": clean_value(item_data.get('Location')),
            "client_name": clean_value(item_data.get('Client')),
            "setup_date": clean_date(item_data.get('SetupDate')),
            "project_name": clean_value(item_data.get('ProjectName')),
            "event_date": clean_date(item_data.get('EventDate')),
            "submitted_by": "inventory-admin",
            
            # Inventory information
            "inventory_items": [
                {
                    "zone_active": clean_value(item_data.get('zone_activity')),
                    "sno": clean_value(item_data.get('sr_no')),
                    "name": clean_value(item_data.get('inventory')),
                    "description": clean_value(item_data.get('description')),
                    "quantity": clean_number_str(item_data.get('quantity')),
                    "comments": clean_value(item_data.get('comments')),
                    "total": clean_number_str(item_data.get('total')),
                    "unit": clean_value(item_data.get('Units')),
                    "per_unit_power": clean_number_str(item_data.get('power_per_unit')),
                    "total_power": clean_number_str(item_data.get('total_power')),
                    "status": clean_value(item_data.get('status')),
                    "poc": clean_value(item_data.get('poc'))
                }
            ]
        }

        # Remove None values to keep payload clean
        payload = {k: v for k, v in payload.items() if v is not None}

        logger.debug(f"Sending payload: {payload}")

        # API request
        response = requests.post(
            url="http://localhost:8000/api/v1/to_event-create-item/",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        # Handle response
        if response.status_code == 422:
            errors = response.json().get('detail', [])
            error_msgs = "\n".join(
                f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg', 'Unknown error')}"
                for e in errors if isinstance(e, dict)
            )
            raise Exception(f"Validation errors:\n{error_msgs}")
            
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        logger.error(f"Error adding item: {str(e)}")
        raise Exception(f"Could not add inventory item: {str(e)}")
    
# Search for Project with there inventory list by [Project_id] by clicking search
def search_project_details_by_id(project_id: str = None) -> List[Dict]:
    """Fetch inventory data filtered by a single ID from the API"""
    try:
        # Validate that exactly one ID is provided
        provided_ids = [id for id in [project_id] if id]
        if len(provided_ids) != 1:
            raise ValueError("Please provide exactly one ID (Project ID) for searching")
        
        # Prepare query parameters
        params = {}
        if project_id:
            params['project_id'] = project_id

        # Make the API request with the parameter
        response = requests.get(
            "http://localhost:8000/api/v1/search-to-event-inventory/",
            params=params
        )
        response.raise_for_status()
        
        # Map backend fields to frontend display names
        formatted_data = []
        for item in response.json():
            formatted_item = {
                'project_id': item.get('work_id', 'N/A'),
                'employee_name': item.get('employee_name', 'N/A'),
                'location': item.get('location', 'N/A'),
                'client_name': item.get('client_name', 'N/A'),
                'setup_date': item.get('setup_date', 'N/A'),
                'project_name': item.get('project_name', 'N/A'),
                'event_date': item.get('event_date', 'N/A'),
                'inventory_items': [
                    {
                        'zone_activity': item.get('inventory_items')[0].get('zone_activity', 'N/A'),
                        'sr_no': item.get('inventory_items')[0].get('sr_no', 'N/A'),
                        'inventory': item.get('inventory_items')[0].get('inventory', 'N/A'),
                        'description': item.get('inventory_items')[0].get('description', 'N/A'),
                        'quantity': item.get('inventory_items')[0].get('quantity', 'N/A'),
                        'comments': item.get('inventory_items')[0].get('comments', 'N/A'),
                        'total': item.get('inventory_items')[0].get('total', 'N/A'),
                        'units': item.get('inventory_items')[0].get('units', 'N/A'),
                        'power_per_unit': item.get('inventory_items')[0].get('power_per_unit', 'N/A'),
                        'total_power': item.get('inventory_items')[0].get('total_power', 'N/A'),
                        'status': item.get('inventory_items')[0].get('status', 'N/A'),
                        'poc': item.get('inventory_items')[0].get('poc', 'N/A')
                    }
                ]
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch inventory by ID: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data")
        return []
    except ValueError as e:
        logger.error(f"Search validation error: {e}")
        messagebox.showwarning("Search Error", str(e))
        return []