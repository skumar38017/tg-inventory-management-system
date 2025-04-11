# front-end/app/api_request/assign_inventory_api_request.py

import requests
from typing import List, Dict
from datetime import datetime, timedelta, date
import logging
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from ..config import *


logger = logging.getLogger(__name__)

# Format a single assigned inventory item to match the table headers
def format_assigned_inventory_item(item: Dict, include_timestamps: bool = False) -> Dict:
    """Format a single assigned inventory item to match the table headers."""
    formatted = {
        "id": item.get("id", ""),
        "sno": item.get("sno", "N/A"),
        "assigned_to": item.get("assign_to", "N/A"),
        "employee_name": item.get("employee_name", "N/A"),
        "inventory_id": item.get("inventory_id", "N/A"),
        "project_id": item.get("project_id", "N/A"),
        "product_id": item.get("product_id", "N/A"),
        "inventory_name": item.get("inventory_name", "N/A"),
        "description": item.get("description", "N/A"),
        "quantity": item.get("quantity", "N/A"),
        "status": item.get("status", "N/A"),
        "assigned_date": item.get("assigned_date", "N/A"),
        "submission_date": item.get("submission_date", "N/A"),
        "purpose_reason": item.get("purpose_reason", "N/A"),
        "assigned_by": item.get("assign_by", "N/A"),
        "comments": item.get("comment", "N/A"),
        "assignment_return_date": item.get("assignment_return_date", "N/A"),
        "assignment_barcode": item.get("assignment_barcode", "N/A"),
        "zone_activity": item.get("zone_activity", "N/A")
    }

    if include_timestamps:
        formatted.update({
            "created_at": item.get("created_at", ""),
            "updated_at": item.get("updated_at", "")
        })

    return formatted

def search_assigned_inventory_by_id(inventory_id: str = None, project_id: str = None, 
                                     employee_name: str = None, product_id: str = None) -> List[Dict]:
    try:
        params = {}
        if inventory_id: params['inventory_id'] = inventory_id
        if project_id: params['project_id'] = project_id
        if product_id: params['product_id'] = product_id
        if employee_name: params['employee_name'] = employee_name

        response = make_api_request("GET", "search-assigned-inventory/", params=params)
        response.raise_for_status()
        return [format_assigned_inventory_item(item) for item in response.json()]

    except requests.RequestException as e:
        logger.error(f"Failed to fetch assigned inventory: {e}")
        messagebox.showerror("Error", "Could not fetch assigned inventory data")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return []
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch assigned inventory: {e}")
        messagebox.showerror("Error", "Could not fetch assigned inventory data")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return []


def load_submitted_assigned_inventory() -> List[Dict]:
    try:
        response = make_api_request("GET", "list-added-assign-inventory/")
        response.raise_for_status()

        formatted_data = [
            format_assigned_inventory_item(item, include_timestamps=True)
            for item in response.json()
        ]

        formatted_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return formatted_data

    except Exception as e:
        logger.error(f"Could not fetch submitted forms: {str(e)}")
        messagebox.showerror("Error", "Could not fetch submitted forms")
        return []
        
def show_all_assigned_inventory_from_db() -> List[Dict]:
    try:
        response = make_api_request("GET", "show-all-assign-inventory/")
        response.raise_for_status()

        formatted_data = [
            format_assigned_inventory_item(item, include_timestamps=True)
            for item in response.json()
        ]
        formatted_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return formatted_data

    except Exception as e:
        logger.error(f"Could not fetch assigned inventory: {str(e)}")
        messagebox.showerror("Error", "Could not fetch assigned inventory")
        return []
    
def submit_assigned_inventory(data: Dict) -> bool:
    try:
        payload = {
            "employee_name": data.get("employee_name", ""),
            "inventory_id": data.get("inventory_id", ""),
            "assignments": []
        }

        for assignment in data.get("assignments", []):
            payload["assignments"].append({
                "assign_to": assignment.get("assigned_to", ""),
                
                "sno": assignment.get("sno", ""),
                "product_id": assignment.get("product_id", ""),
                "project_id": assignment.get("project_id", ""),
                "zone_activity": assignment.get("zone_activity", ""),
                "inventory_id": assignment.get("inventory_id", ""),
                "inventory_name": assignment.get("inventory_name", ""),
                "description": assignment.get("description", ""),
                "quantity": assignment.get("quantity", ""),
                "status": assignment.get("status", ""),
                "purpose_reason": assignment.get("purpose_reason", ""),
                "assigned_date": assignment.get("assigned_date", ""),
                "submission_date": assignment.get("submission_date", ""),
                "assign_by": assignment.get("assigned_by", ""),
                "comment": assignment.get("comments", ""),
                "assignment_return_date": assignment.get("assignment_return_date", ""),
            })

        response = make_api_request("POST", "assign-inventory/", json=payload)
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
    """Update assigned inventory using employee_name and inventory_id"""
    try:
        # Prepare only the allowed fields for update
        update_data = {
            "assign_to": data.get("assign_to", ""),
            "sno": data.get("sno", ""),
            "zone_activity": data.get("zone_activity", ""),
            "description": data.get("description", ""),
            "quantity": data.get("quantity", "1"),
            "status": data.get("status", "assigned"),
            "purpose_reason": data.get("purpose_reason", ""),
            "assign_by": data.get("assign_by", ""),
            "comment": data.get("comment", ""),
            "submission_date": data.get("submission_date", datetime.now().isoformat()),
            "assigned_date": data.get("assigned_date", datetime.now().strftime('%Y-%m-%d')),
            "assignment_return_date": data.get("assignment_return_date", (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        }
        
        # Remove empty date fields
        for date_field in ['submission_date', 'assigned_date', 'assignment_return_date']:
            if not update_data[date_field]:
                update_data.pop(date_field)
        
        logger.debug(f"Sending update data: {update_data}")
        
        response = make_api_request(
            "PUT", 
            f"update-assigned-inventory/{employee_name}/{inventory_id}/",
            json=update_data,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return True
    
    except requests.HTTPError as e:
        if e.response.status_code == 422:
            validation_errors = e.response.json().get('detail', 'Unknown validation error')
            logger.error(f"Validation errors: {validation_errors}")
        logger.error(f"Failed to update assigned inventory: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during update: {e}")
        return False
    
def get_assigned_inventory_by_id(inventory_id: str) -> Dict:
    try:
        response = make_api_request("GET", f"get-assigned-inventory/{inventory_id}/")
        response.raise_for_status()
        return format_assigned_inventory_item(response.json())

    except requests.RequestException as e:
        logger.error(f"Failed to fetch assigned inventory: {e}")
        messagebox.showerror("Error", "Could not fetch assigned inventory data")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return {}  
    
def delete_assigned_inventory(record_id: str) -> bool:
    """Delete an assigned inventory record by its ID"""
    try:
        response = make_api_request(
            "DELETE",
            f"delete-assigned-inventory/{record_id}/"
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to delete assigned inventory: {e}")
        messagebox.showerror("Error", "Could not delete assigned inventory data")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return False