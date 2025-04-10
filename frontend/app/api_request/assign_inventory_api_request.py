# front-end/app/api_request/assign_inventory_api_request.py

import requests
from typing import List, Dict
import logging
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from ..config import *


logger = logging.getLogger(__name__)

def format_assigned_inventory_item(item: Dict, include_timestamps: bool = False) -> Dict:
    """Format a single assigned inventory item to match the table headers.
    
    Args:
        item: The raw inventory item from the API
        include_timestamps: Whether to include updated_at/created_at fields
        
    Returns:
        Formatted dictionary with all required fields
    """
    """Format inventory item for display"""
    formatted = {
            "id": item.get("id", ""),
            "assigned_to": item.get("assign_to", "N/A"),  # Note field name difference
            "employee_name": item.get("employee_name", "N/A"),
            "zone_activity": item.get("zone_activity", "N/A"),
            "sr_no": item.get("sno", "N/A"),  # Note field name difference
            "inventory_id": item.get("inventory_id", "N/A"),
            "product_id": item.get("product_id", "N/A"),
            "project_id": item.get("project_id", "N/A"),
            "inventory_name": item.get("inventory_name", "N/A"),
            "description": item.get("description", "N/A"),
            "quantity": item.get("quantity", "N/A"),
            "status": item.get("status", "N/A"),
            "purpose": item.get("purpose_reason", "N/A"),  # Note field name difference
            "assigned_date": item.get("assigned_date", "N/A"),
            "submission_date": item.get("submission_date", "N/A"),
            "assigned_by": item.get("assign_by", "N/A"),  # Note field name difference
            "comments": item.get("comment", "N/A"),  # Note field name difference
            "assignment_returned_date": item.get("assignment_return_date", "N/A")  # Note field name difference
        }
        
    if include_timestamps:
        formatted.update({
            "created_at": item.get("created_at", ""),
            "updated_at": item.get("updated_at", "")
        })
        
    return formatted

def search_assigned_inventory_by_id(inventory_id: str = None, project_id: str = None, 
                                  employee_name: str = None, product_id: str = None) -> List[Dict]:
    """Fetch inventory data filtered by search criteria from the API"""
    try:
        # Prepare query parameters
        params = {}
        if inventory_id:
            params['inventory_id'] = inventory_id
        if project_id:
            params['project_id'] = project_id
        if product_id:
            params['product_id'] = product_id
        if employee_name:
            params['employee_name'] = employee_name
        
        # Make the API request with the parameters
        response = make_api_request(
            "GET",
            "search-assigned-inventory/",
            params=params
        )
        response.raise_for_status()
        
        # Format the response data using the common formatter
        return [format_assigned_inventory_item(item) for item in response.json()]
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch assigned inventory: {e}")
        messagebox.showerror("Error", "Could not fetch assigned inventory data")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return []

def load_submitted_assigned_inventory() -> List[Dict]:
    """Fetch submitted forms from the API and return sorted by updated_at"""
    try:
        response = make_api_request(
            "GET",
            "list-added-assign-inventory/"
        )
        response.raise_for_status()
        
        # Format each item with timestamps
        formatted_data = [
            format_assigned_inventory_item(item, include_timestamps=True) 
            for item in response.json()
        ]
        
        # Sort by updated_at in descending order (newest first)
        formatted_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return formatted_data
        
    except Exception as e:
        error_msg = "Could not fetch submitted forms"
        logger.error(f"{error_msg}: {str(e)}")
        messagebox.showerror("Error", error_msg)
        return []

def show_all_assigned_inventory_from_db() -> List[Dict]:
    """Fetch all assigned inventory data from the API"""
    try:
        response = make_api_request(
            "GET",
            "show-all-assign-inventory/"
        )
        response.raise_for_status()
        
        # Format each item with timestamps
        formatted_data = [
            format_assigned_inventory_item(item, include_timestamps=True)
            for item in response.json()
        ]
        
        # Sort by updated_at in descending order (newest first)
        formatted_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return formatted_data
        
    except Exception as e:
        error_msg = "Could not fetch assigned inventory"
        logger.error(f"{error_msg}: {str(e)}")
        messagebox.showerror("Error", error_msg)
        return []

def submit_assigned_inventory(data: Dict) -> bool:
    """Submit assigned inventory data to the API"""
    try:
        # Prepare the payload
        payload = {
            "employee_name": assignment.get("employee_name"),
            "inventory_id": data.get("inventory_id"),
            "assignments": []
        }
        
        # Process each assignment
        for assignment in data.get("assignments", []):
            payload["assignments"].append({
                "product_id": data.get("product_id"),
                "project_id": data.get("project_id"),
                "assigned_to": assignment.get("assigned_to"),
                "zone_activity": assignment.get("zone_activity"),
                "sr_no": assignment.get("sr_no"),
                "inventory_id": assignment.get("inventory_id"),
                "product_id": assignment.get("product_id"),
                "project_id": assignment.get("project_id"),
                "inventory_name": assignment.get("inventory_name"),
                "description": assignment.get("description"),
                "quantity": assignment.get("quantity"),
                "status": assignment.get("status"),
                "purpose": assignment.get("purpose"),
                "assigned_date": assignment.get("assigned_date"),
                "submission_date": assignment.get("submission_date"),
                "assigned_by": assignment.get("assigned_by"),
                "comments": assignment.get("comments"),
                "assignment_returned_date": assignment.get("assignment_returned_date")
            })
        
        # Make the API request
        response = make_api_request(
            "POST",
            "assign-inventory/",
            json=payload
        )
        response.raise_for_status()
        
        return True
        
    except requests.RequestException as e:
        logger.error(f"Failed to submit assigned inventory: {e}")
        messagebox.showerror("Error", "Could not submit assigned inventory data")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during submission: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return False
    
# UPDATE: update/edit an existing Assigned Inventory by [EmployeeName, InventoryID]
def update_assigned_inventory(employee_name: str, inventory_id: str, data: Dict) -> bool:
    """Update an existing assigned inventory by employee_name and inventory_id"""
    try:
        # Prepare the payload
        payload = {
            "inventory_id": inventory_id,
            "employee_name": employee_name,
            **data
        }
        
        # Make the API request
        response = make_api_request(
            "PUT",
            "update-assigned-inventory/",
            json=payload
        )
        response.raise_for_status()
        
        return True
        
    except requests.RequestException as e:
        logger.error(f"Failed to update assigned inventory: {e}")
        messagebox.showerror("Error", "Could not update assigned inventory data")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during update: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return False

# GET: Get an assigned inventory by its employee_name and inventory_id
def get_assigned_inventory_by_id(inventory_id: str) -> Dict:
    """Fetch assigned inventory data from the API"""
    try:
        response = make_api_request(
            "GET",
            "get-assigned-inventory/{id}/",
        )
        response.raise_for_status()
        
        # Format the response data using the common formatter
        return format_assigned_inventory_item(response.json())
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch assigned inventory: {e}")
        messagebox.showerror("Error", "Could not fetch assigned inventory data")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return {}   