#  frontend/app/api_request/damage_inventory_api_request.py

import requests
from typing import List, Dict
from datetime import datetime, timedelta, date
import logging
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from config import *
import traceback
from utils.inventory_utils import format_wastage_inventory_item 


logger = logging.getLogger(__name__)

def search_wastage_inventory_by_id(
    inventory_id: str = None, 
    project_id: str = None, 
    product_id: str = None
) -> List[Dict]:
    """
    Enhanced search function for assigned inventory with better parameter handling and error reporting.
    
    Args:
        inventory_id: Inventory ID (with or without INV prefix)
        project_id: Project ID (with or without PRJ prefix)
        employee_name: Employee name (partial matches supported)
        product_id: Product ID (with or without PRD prefix)
    
    Returns:
        List of properly formatted inventory items
        Empty list on error with error message shown to user
    """
    try:
        # Normalize and validate parameters
        params = {}
        
        def normalize_id(id_value, prefix):
            """Normalize ID by removing prefix if present and ensuring uppercase"""
            if not id_value:
                return None
            id_value = str(id_value).strip().upper()
            return id_value.replace(prefix, "") if id_value.startswith(prefix) else id_value

        if inventory_id:
            params['inventory_id'] = normalize_id(inventory_id, "INV")
        if project_id:
            params['project_id'] = normalize_id(project_id, "PRJ")
        if product_id:
            params['product_id'] = normalize_id(product_id, "PRD")
        if not params:
            raise ValueError("Please provide at least one search parameter")

        # API request with timeout
        response = make_api_request(
            "GET", 
            "search-wastage-inventory/",
            params=params,
            timeout=30  # 30 second timeout
        )
        
        # Check for empty response
        if not response.content:
            raise ValueError("Server returned empty response")

        response.raise_for_status()
        results = response.json()

        # Process and validate results
        if not isinstance(results, list):
            raise ValueError(f"Unexpected response format. Expected list, got {type(results)}")

        formatted_results = []
        error_count = 0
        
        for item in results:
            formatted = format_wastage_inventory_item(item)
            if "error" not in formatted:
                formatted_results.append(formatted)
            else:
                error_count += 1

        if error_count:
            logger.warning(f"Skipped {error_count} malformed items in search results")

        if not formatted_results:
            messagebox.showinfo("No Results", "No matching inventory items found")
            
        return formatted_results

    except requests.exceptions.Timeout:
        error_msg = "Search timed out. Please try again later."
        logger.error(error_msg)
        messagebox.showerror("Timeout Error", error_msg)
        return []
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error during search: {str(e)}"
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json().get('detail', 'No details')
                error_msg += f"\nServer response: {error_detail}"
            except:
                error_msg += f"\nStatus code: {e.response.status_code}"
        logger.error(error_msg)
        messagebox.showerror("Search Error", error_msg)
        return []
    except ValueError as ve:
        logger.error(f"Invalid search parameters: {ve}")
        messagebox.showwarning("Invalid Search", str(ve))
        return []
    except Exception as e:
        logger.error(f"Unexpected search error: {str(e)}\n{traceback.format_exc()}")
        messagebox.showerror("Error", "An unexpected error occurred during search")
        return []

def load_submitted_wastage_inventory() -> List[Dict]:
    try:
        response = make_api_request("GET", "list-added-wastage-inventory/")
        response.raise_for_status()

        formatted_data = [
            format_wastage_inventory_item(item, include_timestamps=True)
            for item in response.json()
        ]

        formatted_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return formatted_data

    except Exception as e:
        logger.error(f"Could not fetch submitted forms: {str(e)}")
        messagebox.showerror("Error", "Could not fetch submitted forms")
        return []
        
def show_all_wastage_inventory() -> List[Dict]:
    try:
        response = make_api_request("GET", "show-all-wastage-inventory/")
        response.raise_for_status()

        formatted_data = [
            format_wastage_inventory_item(item, include_timestamps=True)
            for item in response.json()
        ]
        formatted_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return formatted_data

    except Exception as e:
        logger.error(f"Could not fetch assigned inventory: {str(e)}")
        messagebox.showerror("Error", "Could not fetch assigned inventory")
        return []
    
def submit_wastage_inventory(data: Dict) -> bool:
    try:
        # Prepare payload for each wastage
        wastages = []
        for wastage in data.get('wastages', []):
            payload = {
                "assign_to": wastage.get("assign_to", ""),
                "sno": wastage.get("sno", ""),
                "employee_name": wastage.get("employee_name", ""),
                "inventory_id": wastage.get("inventory_id", ""),
                "project_id": wastage.get("project_id", ""),
                "product_id": wastage.get("product_id", ""),
                "inventory_name": wastage.get("inventory_name", ""),
                "description": wastage.get("description", ""),
                "quantity": wastage.get("quantity", "1"),
                "status": wastage.get("status", ""),
                "receive_date": wastage.get("receive_date", datetime.now().strftime('%Y-%m-%d')),
                "receive_by": wastage.get("receive_by", ""),
                "check_status": wastage.get("check_status", ""),
                "location": wastage.get("location", ""),
                "project_name": wastage.get("project_name", ""),
                "event_date": wastage.get("event_date", datetime.now().strftime('%Y-%m-%d')),
                "comment": wastage.get("comment", ""),
                "zone_activity": wastage.get("zone_activity", ""),
                "wastage_reason": wastage.get("wastage_reason", ""),
                "wastage_date": wastage.get("wastage_date", datetime.now().strftime('%Y-%m-%d')),
                "wastage_approved_by": wastage.get("wastage_approved_by", ""),
                "wastage_status": wastage.get("wastage_status", ""),
            }
            wastages.append(payload)
            logger.debug(f"Submitting payload: {json.dumps(payload, indent=2)}")

        # Submit each wastage individually
        for payload in wastages:
            response = make_api_request("POST", "create-wastage-inventory/", json=payload)
            response.raise_for_status()
            
        return True

    except requests.RequestException as e:
        logger.error(f"API request failed to {e.request.url}: {e}")
        logger.error(f"Response content: {e.response.text if e.response else 'No response'}")
        messagebox.showerror("Error", f"Failed to submit data: {e}")
        return False
    except Exception as e:
        
        logger.error(f"Unexpected error during submission: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return False
            
# UPDATE: update/edit an existing Assigned Inventory by [EmployeeName, InventoryID]
def update_wastage_inventory(employee_name: str, inventory_id: str, data: Dict) -> bool:
    """Update assigned inventory using employee_name and inventory_id"""
    try:
        # Prepare only the allowed fields for update
        update_data = {
            "assign_to": data.get("assign_to", ""),
            "sno": data.get("sno", ""),
            "description": data.get("description", ""),
            "quantity": data.get("quantity", "1"),  # Always set quantity to 1
            "status": data.get("status", "assigned"),  # Always set status to assigned
            "receive_date": data.get("receive_date", ""),  # Always set receive_date to empty
            "receive_by": data.get("receive_by", ""),  # Always set receive_by to empty
            "check_status": data.get("check_status", ""),  # Always set check_status to empty
            "location": data.get("location", ""),  # Always set location to empty
            "project_name": data.get("project_name", ""),  # Always set project_name to empty
            "comment": data.get("comment", ""),  # Always set comment to empty
            "zone_activity": data.get("zone_activity", ""),  # Always set zone_activity to empty
            "wastage_reason": data.get("wastage_reason", ""),  # Always set wastage_reason to empty
            "wastage_date": data.get("wastage_date", ""),  # Always set wastage_date to empty
            "wastage_approved_by": data.get("wastage_approved_by", ""),  # Always set wastage_approved_by to empty
            "wastage_status": data.get("wastage_status", ""),  # Always set wastage_status to empty
        }
               
        logger.debug(f"Sending update data: {update_data}")
        
        response = make_api_request(
            "PUT", 
            f"update-wastage-inventory/{employee_name}/{inventory_id}/",
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
    
def get_wastage_inventory_by_id(inventory_id: str, employee_name: str) -> Dict:
    try:
        response = make_api_request("GET", f"get-wastage-inventory/{employee_name}/{inventory_id}/")
        response.raise_for_status()
        return format_wastage_inventory_item(response.json())

    except requests.RequestException as e:
        logger.error(f"Failed to fetch assigned inventory: {e}")
        messagebox.showerror("Error", "Could not fetch assigned inventory data")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return {}  
    
def delete_wastage_inventory(employee_name: str, inventory_id: str) -> bool:
    """Delete an wastage inventory record by its ID"""
    try:
        response = make_api_request(
            "DELETE",
            f"delete-wastage-inventory/{employee_name}/{inventory_id}/"
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
    
