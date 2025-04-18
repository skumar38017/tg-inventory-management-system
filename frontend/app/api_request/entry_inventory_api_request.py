#  frontend/app/entry_inventory_functions_request.py
import requests
from typing import List, Dict, Any
import logging
import tkinter as tk
import uuid
import re
from tkinter import messagebox
from datetime import datetime, timezone, date
from ..config import *

logger = logging.getLogger(__name__)

def format_inventory_item(item: Dict[str, Any]) -> Dict[str, str]:
    """Helper function to format inventory item data consistently across all functions."""
    # Helper function to handle null/empty values and format them properly
    def get_value(key: str, default: str = 'N/A') -> str:
        value = item.get(key)
        if value is None or str(value).lower() in ('', 'null', 'none'):
            return default
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        if isinstance(value, str) and value.lower() in ['true', 'false']:
            return 'Yes' if value.lower() == 'true' else 'No'
        return str(value)
    
    return {
        'ID': get_value('id'),
        'Serial No.': get_value('sno'),
        'Product ID': get_value('product_id'),
        'InventoryID': get_value('inventory_id'),
        'Name': get_value('inventory_name'),
        'Material': get_value('material'),
        'Total Quantity': get_value('total_quantity', '0'),
        'Manufacturer': get_value('manufacturer'),
        'Purchase Dealer': get_value('purchase_dealer'),
        'Purchase Date': get_value('purchase_date'),
        'Purchase Amount': get_value('purchase_amount', '0.00'),
        'Repair Quantity': get_value('repair_quantity', '0'),
        'Repair Cost': get_value('repair_cost', '0.00'),
        'On Rent': get_value('on_rent'),
        'Vendor Name': get_value('vendor_name'),
        'Total Rent': get_value('total_rent', '0.00'),
        'Rented Inventory Returned': get_value('rented_inventory_returned'),
        'Returned Date': get_value('returned_date'),
        'On Event': get_value('on_event'),
        'In Office': get_value('in_office'),
        'In Warehouse': get_value('in_warehouse'),
        'Issued Qty': get_value('issued_qty', '0'),
        'Balance Qty': get_value('balance_qty', '0'),
        'Submitted By': get_value('submitted_by'),
        'Created At': get_value('created_at'),
        'Updated At': get_value('updated_at'),
        'BarCode': get_value('inventory_barcode'),
        'BacodeUrl': get_value('inventory_barcode_url'),
    }

def format_inventory_response(response_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Helper function to format a list of inventory items from API response."""
    return [format_inventory_item(item) for item in response_data]

def handle_api_error(error: Exception, action: str, show_error: bool = True) -> None:
    """Helper function to handle API errors consistently."""
    logger.error(f"Failed to {action}: {error}")
    if show_error:
        messagebox.showerror("Error", f"Could not {action}")

#  ------------------------------------------------------------------------------------------------
#   Now the original functions can be simplified using these helpers:
#  ------------------------------------------------------------------------------------------------

#  Sync inventory data from the API by `sync` button
def sync_inventory() -> List[Dict[str, str]]:
    """Fetch inventory data from the API and return formatted data"""
    try:
        response = make_api_request("POST", "/sync-from-sheets/")
        response.raise_for_status()
        return format_inventory_response(response.json())
    except requests.RequestException as e:
        handle_api_error(e, "Sync inventory")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during sync: {str(e)}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return []
    

#  Filter inventory by date range by `filter` button
def filter_inventory_by_date_range(from_date: str, to_date: str) -> List[Dict[str, str]]:
    """Fetch inventory data filtered by date range from the API"""
    try:
        response = make_api_request(
            "GET",
            "date-range/",
            params={"from_date": from_date, "to_date": to_date}
        )
        response.raise_for_status()
        return format_inventory_response(response.json())
    except requests.RequestException as e:
        handle_api_error(e, "fetch inventory by date range")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {str(e)}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return []
    
#  Show all inventory from local database by clicking the `Show All` button
def show_all_inventory() -> List[Dict[str, str]]:
    """Show all inventory from local database"""
    try:
        response = make_api_request("GET", "show-all/")
        response.raise_for_status()
        return format_inventory_response(response.json())
    except requests.RequestException as e:
        handle_api_error(e, "fetch all inventory")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {str(e)}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return []
    
# Add new inventory items to the database with proper data formatting
def add_new_inventory_item(item_data: dict):
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
        
        # Helper function for boolean fields
        def clean_boolean(value):
            if value is None:
                return None
            if isinstance(value, bool):
                return value
            if str(value).lower() in ('true', 'yes', '1'):
                return True
            if str(value).lower() in ('false', 'no', '0'):
                return False
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
        product_id = clean_value(item_data.get('ProductID'))
        inventory_id = clean_value(item_data.get('InventoryID'))
        if product_id:
            product_id = ''.join(c for c in product_id if c.isdigit())
        if inventory_id:
            inventory_id = ''.join(c for c in inventory_id if c.isdigit())

        # Payload construction - all fields optional
        payload = {
            # Basic information
            "product_id": product_id,
            "inventory_id": inventory_id,
            "sno": clean_value(item_data.get('Sno')),
            "inventory_name": clean_value(item_data.get('Name')),
            "material": clean_value(item_data.get('Material')),
            "manufacturer": clean_value(item_data.get('Manufacturer')),
            "submitted_by": clean_value(item_data.get('Submitedby')),
            
            # Quantity information (as strings)
            "total_quantity": clean_number_str(item_data.get('TotalQuantity')),
            "issued_qty": clean_number_str(item_data.get('IssuedQty')),
            "balance_qty": clean_number_str(item_data.get('BalanceQty')),
            "repair_quantity": clean_number_str(item_data.get('RepairQuantity')),
            
            # Purchase information
            "purchase_dealer": clean_value(item_data.get('PurchaseDealer')),
            "purchase_date": clean_date(item_data.get('PurchaseDate')),
            "purchase_amount": clean_number_str(item_data.get('PurchaseAmount')),
            "repair_cost": clean_number_str(item_data.get('RepairCost')),
            
            # Rental information
            "vendor_name": clean_value(item_data.get('VendorName')),
            "total_rent": clean_number_str(item_data.get('TotalRent')),
            "returned_date": clean_date(item_data.get('ReturnedDate')),
            
            # Status flags
            "on_rent": clean_boolean(item_data.get('OnRent')),
            "rented_inventory_returned": clean_boolean(item_data.get('RentedInventoryReturned')),
            "on_event": clean_boolean(item_data.get('OnEvent')),
            "in_office": clean_boolean(item_data.get('InOffice')),
            "in_warehouse": clean_boolean(item_data.get('InWarehouse'))
        }

        # Remove None values to keep payload clean
        payload = {k: v for k, v in payload.items() if v is not None}

        logger.debug(f"Sending payload: {payload}")

        # API request
        response = make_api_request(
            "POST",
            "create-item/",
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
    
# Search for an item by [inventory_id, product_id, Project_id] by clicking search
def search_inventory_by_id(inventory_id: str = None, product_id: str = None) -> List[Dict[str, str]]:
    """Fetch inventory data filtered by a single ID from the API"""
    try:
        provided_ids = [id for id in [inventory_id, product_id] if id]
        if len(provided_ids) != 1:
            raise ValueError("Please provide exactly one ID (Inventory ID or Product ID) for searching")
        
        params = {'inventory_id': inventory_id} if inventory_id else {'product_id': product_id}
        response = make_api_request("GET", "search/", params=params)
        response.raise_for_status()
        return format_inventory_response(response.json())
    except requests.RequestException as e:
        handle_api_error(e, "fetch inventory by ID")
        return []
    except ValueError as e:
        logger.error(f"Search validation error: {e}")
        messagebox.showwarning("Search Error", str(e))
        return []
            
async def upload_to_event_data():
    """Trigger upload of Redis data to main database"""
    try:
        response = await make_api_request(
            "POST",
            "to_event-upload-data/",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            uploaded_count = len(response.json())
            messagebox.showinfo("Success", 
                              f"Successfully uploaded {uploaded_count} records")
            return True
        else:
            messagebox.showerror("Error", 
                                "Failed to upload data from Redis")
            return False
            
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        messagebox.showerror("Error", "Failed to connect to upload service")
        return False
    
# #  Search  Project by [Project_id] by clicking search
# def search_project_details_by_project_id(project_id: str) -> List[Dict]:
#     """Fetch inventory data filtered by a single project_id from the API"""
#     if not project_id or not str(project_id).strip():
#         logger.error("Empty project_id provided for search")
#         messagebox.showwarning("Search Error", "Project ID is required for searching")
#         return []
    
#     try:
#         # Ensure project_id has proper PRJ prefix if missing
#         project_id = project_id.upper()
#         if not project_id.startswith('PRJ'):
#             project_id = f'PRJ{project_id}'
            
#         response = make_api_request(
#             "GET",
#             f"to_event-search-entries-by-project-id/{project_id}/"
#         )
        
#         if response.status_code == 404:
#             logger.debug(f"Project {project_id} not found")
#             return []
            
#         response.raise_for_status()
#         logger.debug(f"Raw API response for {project_id}: {response.text}")
        
#         data = response.json()
        
#         if isinstance(data, dict):
#             return [format_project_item(data)]
#         elif isinstance(data, list):
#             return [format_project_item(item) for item in data]
#         else:
#             logger.error(f"Unexpected API response format: {type(data)}")
#             return []
            
#     except Exception as e:
#         error_msg = f"Could not fetch project data: {str(e)}"
#         logger.error(error_msg, exc_info=True)
#         messagebox.showerror("Error", error_msg)
#         return []
    
# # Format project item from API response to consistent frontend format
# def format_project_item(item: dict) -> dict:
#     """Format project item from API response to consistent frontend format"""
#     if not isinstance(item, dict):
#         logger.error(f"Invalid item format: {type(item)}")
#         return {}
        
#     # Handle both flat structure (old) and nested inventory_items (new)
#     inventory_items = item.get('inventory_items', [])
#     if not inventory_items:
#         # Convert flat structure to nested if needed
#         inventory_item = {
#             'project_id': item.get('work_id') or item.get('project_id'),
#             'zone_active': item.get('zone_active'),
#             'sno': item.get('sno'),
#             'name': item.get('inventory_name'),
#             'description': item.get('description'),
#             'quantity': item.get('quantity'),
#             'material': item.get('material'),
#             'comments': item.get('comments'),
#             'total': item.get('total'),
#             'unit': item.get('unit'),
#             'per_unit_power': item.get('per_unit_power'),
#             'total_power': item.get('total_power'),
#             'status': item.get('status'),
#             'poc': item.get('poc')
#         }
#         inventory_items = [inventory_item] if any(inventory_item.values()) else []
    
#     return {
#         'id': item.get('id'),
#         'work_id': item.get('project_id') or item.get('work_id'),
#         'employee_name': item.get('employee_name'),
#         'location': item.get('location'),
#         'client_name': item.get('client_name'),
#         'setup_date': item.get('setup_date'),
#         'project_name': item.get('project_name'),
#         'event_date': item.get('event_date'),
#         'inventory_items': inventory_items,
#         'submitted_by': item.get('submitted_by'),
#         'barcode': item.get('project_barcode'),
#         'updated_at': item.get('updated_at')
#     }