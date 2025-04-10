#  front-end/app/api_request/assign_inventory_api_request.py

import requests
from typing import List, Dict
import logging
import tkinter as tk
import uuid
import re
from tkinter import messagebox
from datetime import datetime, timezone, date
from ..config import *
from typing import Optional, Union


logger = logging.getLogger(__name__)

#  Search Assigned Inventory by [inventory_id, project_id, Project_id, Employee_name] by clicking search
def search_assigned_inventory_by_id(inventory_id: str = None, project_id: str = None, employee_name: str = None, product_id: str = None) -> List[Dict]:
    """Fetch inventory data filtered by a single ID from the API"""
    try:
        # Validate that exactly one ID is provided
        provided_ids = [id for id in [inventory_id, project_id, employee_name, product_id] if id]
        if len(provided_ids) != 1:
            raise ValueError("Please provide exactly one ID (Inventory ID, Project ID, or Employee Name) for searching")
        
        # Prepare query parameters
        params = {}
        if inventory_id:
            params['inventory_id'] = inventory_id
        elif project_id:
            params['project_id'] = project_id
        elif product_id:
            params['product_id'] = product_id
        elif employee_name:
            params['employee_name'] = employee_name
        else:
            raise ValueError("Please provide exactly one ID (Inventory ID, Project ID, or Employee Name) for searching")
        
        # Make the API request with the parameter
        response = make_api_request(
            "GET",
            f"search-assigned-inventory/",
            params=params
        )
        response.raise_for_status()
        
        # Map backend fields to frontend display names
        formatted_data = []
        for item in response.json():  
            formatted_item = {
                "Assigned To": item.get('assigned_to', 'N/A'),
                "InventoryID": item.get('inventory_id', 'N/A'),
                "Project ID": item.get('project_id', 'N/A'),
                "Inventory Name": item.get('Inventory Name', 'N/A'),
                "Sr No": item.get('sr_no', 'N/A'),
                "Description": item.get('description', 'N/A'),
                "Qty": item.get('quantity', 'N/A'),
                "Status": item.get('status', 'N/A'),
                "Purpose": item.get('purpose', 'N/A'),
                "Assigned Date": item.get('assigned_date', 'N/A'),
                "Submission Date": item.get('submission_date', 'N/A'),
                "Assigned By": item.get('assigned_by', 'N/A'),
                "Comments": item.get('comments', 'N/A'),
                "Assignment Returned Date": item.get('assignment_returned_date', 'N/A')
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch assigned inventory by ID: {e}")
        messagebox.showerror("Error", "Could not fetch assigned inventory data")
        return []
    except ValueError as e:
        logger.error(f"Search validation error: {e}")
        messagebox.showwarning("Search Error", str(e))
        return []

# READ ALL: List only assigned inventory from local Redis Directly
def load_submitted_assigned_inventory_from_db() -> List[Dict]:
    """Fetch submitted forms from the API and return sorted by updated_at"""
    try:
        response = make_api_request(
            "GET",
            "list-added-assign-inventory/"
        )
        
        # Ensure we have a valid response
        if response.status_code != 200:
            logger.error(f"API returned status code: {response.status_code}")
            return []
            
        assigned_inventory = response.json()
        
        # Validate we got a list of projects
        if not isinstance(assigned_inventory, list):
            logger.error(f"Unexpected API response format: {assigned_inventory}")
            return []
            
        # Format each project and sort by updated_at (newest first)
        formatted_assigned_inventory = []
        for item in assigned_inventory:
            try:
                formatted = format_assigned_inventory_item(item)
                # Ensure updated_at exists (set to empty string if missing)
                formatted['updated_at'] = item.get('updated_at', '')
                formatted_assigned_inventory.append(formatted)
            except Exception as e:
                logger.error(f"Error formatting project item: {str(e)}")
                continue
                
        # Sort by updated_at in descending order (newest first)
        formatted_assigned_inventory.sort(
            key=lambda x: x.get('updated_at', ''),
            reverse=True
        )
        
        return formatted_assigned_inventory
        
    except Exception as e:
        error_msg = "Could not fetch submitted forms"
        logger.error(f"{error_msg}: {str(e)}")
        messagebox.showerror("Error", error_msg)
        return []

# READ ALL: Show All Assigned Inventory from local redis directly 
def show_all_assigned_inventory_from_db() -> List[Dict]:
    """Fetch assigned inventory data from the API and return"""
    try:
        response = make_api_request(
            "GET",
            "show-all-assign-inventory/"
        )
        
        # Ensure we have a valid response
        if response.status_code != 200:
            logger.error(f"API returned status code: {response.status_code}")
            return []
            
        assigned_inventory = response.json()
        
        # Validate we got a list of projects
        if not isinstance(assigned_inventory, list):
            logger.error(f"Unexpected API response format: {assigned_inventory}")
            return []
            
        # Format each project and sort by updated_at (newest first)
        formatted_assigned_inventory = []
        for item in assigned_inventory:
            try:
                formatted = format_assigned_inventory_item(item)
                # Ensure updated_at exists (set to empty string if missing)
                formatted['updated_at'] = item.get('updated_at', '')
                formatted_assigned_inventory.append(formatted)
            except Exception as e:
                logger.error(f"Error formatting project item: {str(e)}")
                continue
                
        # Sort by updated_at in descending order (newest first)
        formatted_assigned_inventory.sort(
            key=lambda x: x.get('updated_at', ''),
            reverse=True
        )
        
        return formatted_assigned_inventory
        
    except Exception as e:
        error_msg = "Could not fetch submitted forms"
        logger.error(f"{error_msg}: {str(e)}")
        messagebox.showerror("Error", error_msg)    
        return []

def format_assigned_inventory_item(item: dict) -> dict:
    """Format project item from API response to frontend format"""
    # Handle both flat structure (old) and nested inventory_items (new)
    if not isinstance(item, dict):
        logger.error(f"Invalid item format: {type(item)}")
        return {}
        
    if 'inventory_items' not in item:
        # Convert flat structure to nested
            inventory_items = {
                "Assigned To": item.get('assigned_to', 'N/A'),
                "Employee Name": item.get('employee_name', 'N/A'),
                "InventoryID": item.get('inventory_id', 'N/A'),
                "Project ID": item.get('project_id', 'N/A'),
                "Inventory Name": item.get('Inventory Name', 'N/A'),
                "Sr No": item.get('sr_no', 'N/A'),
                "Description": item.get('description', 'N/A'),
                "Qty": item.get('quantity', 'N/A'),
                "Status": item.get('status', 'N/A'),
                "Purpose": item.get('purpose', 'N/A'),
                "Assigned Date": item.get('assigned_date', 'N/A'),
                "Submission Date": item.get('submission_date', 'N/A'),
                "Assigned By": item.get('assigned_by', 'N/A'),
                "Comments": item.get('comments', 'N/A'),
                "Assignment Returned Date": item.get('assignment_returned_date', 'N/A')
            }
            inventory_items = [inventory_items]
    else:
        inventory_items = item.get('inventory_items', [])
    
    return {    "id": item.get('id'),
                "Assigned To": item.get('assigned_to', 'N/A'),
                "Employee Name": item.get('employee_name', 'N/A'),
                "InventoryID": item.get('inventory_id', 'N/A'),
                "Project ID": item.get('project_id', 'N/A'),
                "Inventory Name": item.get('Inventory Name', 'N/A'),
                "Sr No": item.get('sr_no', 'N/A'),
                "Description": item.get('description', 'N/A'),
                "Qty": item.get('quantity', 'N/A'),
                "Status": item.get('status', 'N/A'),
                "Purpose": item.get('purpose', 'N/A'),
                "Assigned Date": item.get('assigned_date', 'N/A'),
                "Submission Date": item.get('submission_date', 'N/A'),
                "Assigned By": item.get('assigned_by', 'N/A'),
                "Comments": item.get('comments', 'N/A'),
                "Assignment Returned Date": item.get('assignment_returned_date', 'N/A'),
                "inventory_barcode": item.get('inventory_barcode', 'N/A'),
                "inventory_barcode_unique_code": item.get('inventory_barcode_unique_code', 'N/A'),
                "updated_at": item.get('updated_at', 'N/A'),
                "created_at": item.get('created_at', 'N/A')
            }