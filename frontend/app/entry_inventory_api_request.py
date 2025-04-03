#  frontend/app/entry_inventory_functions_request.py
import requests
from typing import List, Dict
import logging
import uuid
import re
from tkinter import messagebox
from datetime import datetime, timezone, date

logger = logging.getLogger(__name__)

#  Sync inventory data from the API by `sync` button
def sync_inventory() -> List[Dict]:
    """Fetch inventory data from the API and return formatted data"""
    try:
        response = requests.get("http://localhost:8000/api/v1/show-all/")
        response.raise_for_status()
        
        # Map backend fields to frontend display names
        formatted_data = []
        for item in response.json():
            formatted_item = {
                'ID': item.get('uuid', 'N/A'),
                'Serial No.': item.get('sno', 'N/A'),
                'InventoryID': item.get('inventory_id', 'N/A'),
                'Product ID': item.get('product_id', 'N/A'),
                'Name': item.get('name', 'N/A'),
                'Material': item.get('material', 'N/A'),
                'Total Quantity': item.get('total_quantity', 'N/A'),
                'Manufacturer': item.get('manufacturer', 'N/A'),
                'Purchase Dealer': item.get('purchase_dealer', 'N/A'),
                'Purchase Date': item.get('purchase_date', 'N/A'),
                'Purchase Amount': item.get('purchase_amount', 'N/A'),
                'Repair Quantity': item.get('repair_quantity', 'N/A'),
                'Repair Cost': item.get('repair_cost', 'N/A'),
                'On Rent': item.get('on_rent', 'N/A'),
                'Vendor Name': item.get('vendor_name', 'N/A'),
                'Total Rent': item.get('total_rent', 'N/A'),
                'Rented Inventory Returned': item.get('rented_inventory_returned', 'N/A'),
                'Returned Date': item.get('returned_date', 'N/A'),
                'On Event': item.get('on_event', 'N/A'),
                'In Office': item.get('in_office', 'N/A'),
                'In Warehouse': item.get('in_warehouse', 'N/A'),
                'Issued Qty': item.get('issued_qty', 'N/A'),
                'Balance Qty': item.get('balance_qty', 'N/A'),
                'Submitted By': item.get('submitted_by', 'N/A'),
                'Created At': item.get('created_at', 'N/A'),
                'Updated At': item.get('updated_at', 'N/A'),
                'BarCode': item.get('bar_code', 'N/A'),
                # Add any other fields you want to display
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to Sync inventory: {e}")
        messagebox.showerror("Error", "Could not Sync inventory data")
        return []

#  Filter inventory by date range by `filter` button
def filter_inventory_by_date_range(from_date: str, to_date: str) -> List[Dict]:
    """Fetch inventory data filtered by date range from the API"""
    try:
        # Make the API request with the date strings
        response = requests.get(
            "http://localhost:8000/api/v1/date-range/",
            params={
                "from_date": from_date,
                "to_date": to_date
            }
        )
        response.raise_for_status()
        
        # Map backend fields to frontend display names
        formatted_data = []
        for item in response.json():
            formatted_item = {
                'ID': item.get('uuid', 'N/A'),
                'Serial No.': item.get('sno', 'N/A'),
                'InventoryID': item.get('inventory_id', 'N/A'),
                'Product ID': item.get('product_id', 'N/A'),
                'Name': item.get('name', 'N/A'),
                'Material': item.get('material', 'N/A'),
                'Total Quantity': item.get('total_quantity', 'N/A'),
                'Manufacturer': item.get('manufacturer', 'N/A'),
                'Purchase Dealer': item.get('purchase_dealer', 'N/A'),
                'Purchase Date': item.get('purchase_date', 'N/A'),
                'Purchase Amount': item.get('purchase_amount', 'N/A'),
                'Repair Quantity': item.get('repair_quantity', 'N/A'),
                'Repair Cost': item.get('repair_cost', 'N/A'),                
                'On Rent': item.get('on_rent', 'N/A'),
                'Vendor Name': item.get('vendor_name', 'N/A'),
                'Total Rent': item.get('total_rent', 'N/A'),
                'Rented Inventory Returned': item.get('rented_inventory_returned', 'N/A'),
                'Returned Date': item.get('returned_date', 'N/A'),
                'On Event': item.get('on_event', 'N/A'),
                'In Office': item.get('in_office', 'N/A'),
                'In Warehouse': item.get('in_warehouse', 'N/A'),
                'Issued Qty': item.get('issued_qty', 'N/A'),
                'Balance Qty': item.get('balance_qty', 'N/A'),
                'Submitted By': item.get('submitted_by', 'N/A'),
                'Created At': item.get('created_at', 'N/A'),
                'Updated At': item.get('updated_at', 'N/A'),
                'BarCode': item.get('bar_code', 'N/A'),
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch inventory by date range: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data by date range")
        return []
    
#  Show all inventory from local database by clicking the `Show All` button
def show_all_inventory():
    """Show all inventory from local database"""
    try:
        response = requests.get("http://localhost:8000/api/v1/show-all/")
        response.raise_for_status()
        
        # Map backend fields to frontend display names
        formatted_data = []
        for item in response.json():
            formatted_item = {
                'ID': item.get('uuid', 'N/A'),
                'Serial No.': item.get('sno', 'N/A'),
                'InventoryID': item.get('inventory_id', 'N/A'),
                'Product ID': item.get('product_id', 'N/A'),
                'Name': item.get('name', 'N/A'),
                'Material': item.get('material', 'N/A'),
                'Total Quantity': item.get('total_quantity', 'N/A'),
                'Manufacturer': item.get('manufacturer', 'N/A'),                
                'Purchase Dealer': item.get('purchase_dealer', 'N/A'),
                'Purchase Date': item.get('purchase_date', 'N/A'),
                'Purchase Amount': item.get('purchase_amount', 'N/A'),
                'Repair Quantity': item.get('repair_quantity', 'N/A'),
                'Repair Cost': item.get('repair_cost', 'N/A'),
                'On Rent': item.get('on_rent', 'N/A'),
                'Vendor Name': item.get('vendor_name', 'N/A'),
                'Total Rent': item.get('total_rent', 'N/A'),
                'Rented Inventory Returned': item.get('rented_inventory_returned', 'N/A'),
                'Returned Date': item.get('returned_date', 'N/A'),
                'On Event': item.get('on_event', 'N/A'),
                'In Office': item.get('in_office', 'N/A'),
                'In Warehouse': item.get('in_warehouse', 'N/A'),
                'Issued Qty': item.get('issued_qty', 'N/A'),
                'Balance Qty': item.get('balance_qty', 'N/A'),
                'Submitted By': item.get('submitted_by', 'N/A'),
                'Created At': item.get('created_at', 'N/A'),
                'Updated At': item.get('updated_at', 'N/A'),
                'BarCode': item.get('bar_code', 'N/A'),
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch inventory by date range: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data by date range")
        return []

# Add new inventory items to the database with proper data formatting
def add_new_inventory_item(item_data: dict):
    """Add new inventory items to the database with proper data formatting"""
    try:
        # Helper function to safely get and strip string values
        def get_stripped(value, default=''):
            return str(value).strip() if value is not None else default

        # Helper function to format IDs with prefix and validate numbers
        def format_id(value, prefix):
            if not value:
                return prefix + str(uuid.uuid4().hex[:6]).upper()
            
            # Remove any existing prefix and validate numbers
            clean_value = re.sub(r'^[A-Za-z]+', '', str(value))
            if not clean_value.isdigit():
                raise ValueError(f"{prefix} ID must contain only numbers after prefix")
            return prefix + clean_value
        
        # Handle SNO - now optional
        sno = get_stripped(item_data.get('Sno') or item_data.get('sno') or item_data.get('S No'))
        if not sno:
            sno = ''  # Set to empty string if not provided

        # Handle date fields with validation
        def format_date(date_str):
            date_str = get_stripped(date_str)
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date().isoformat()
            except ValueError:
                return None

        purchase_date = format_date(item_data.get('PurchaseDate'))
        returned_date = format_date(item_data.get('ReturnedDate'))

        # Handle numeric fields with validation
        def format_number(num_str, default=0):
            num_str = get_stripped(num_str)
            try:
                return str(float(num_str)) if num_str else str(default)
            except ValueError:
                return str(default)

        # Construct API payload with proper formatting
        api_payload = {
            "product_id": format_id(item_data.get('ProductID'), 'PRD'),
            "inventory_id": format_id(item_data.get('InventoryID'), 'INV'),
            "sno": sno,
            "name": get_stripped(item_data.get('Name')),
            "material": get_stripped(item_data.get('Material')),
            "total_quantity": format_number(item_data.get('TotalQuantity')),
            "manufacturer": get_stripped(item_data.get('Manufacturer')),
            "purchase_dealer": get_stripped(item_data.get('PurchaseDealer')),
            "purchase_date": purchase_date,  # Can be None
            "purchase_amount": format_number(item_data.get('PurchaseAmount')),
            "repair_quantity": format_number(item_data.get('RepairQuantity')),
            "repair_cost": format_number(item_data.get('RepairCost')),
            "on_rent": "true" if item_data.get('OnRent') else "false",
            "vendor_name": get_stripped(item_data.get('VendorName')),
            "total_rent": format_number(item_data.get('TotalRent')),
            "rented_inventory_returned": "true" if item_data.get('RentedInventoryReturned') else "false",
            "returned_date": returned_date,
            "on_event": "true" if item_data.get('OnEvent') else "false",
            "in_office": "true" if item_data.get('InOffice') else "false",
            "in_warehouse": "true" if item_data.get('InWarehouse') else "false",
            "issued_qty": format_number(item_data.get('IssuedQty')),
            "balance_qty": format_number(item_data.get('BalanceQty')),
            "submitted_by": get_stripped(item_data.get('Submitedby')),
        }

        # Remove None values from payload except for required fields
        payload = {k: v for k, v in payload.items() if v is not None}


        logger.debug(f"Sending payload: {api_payload}")

        # API request with enhanced error handling
        response = requests.post(
            url="http://localhost:8000/api/v1/create-item/",
            headers={"Content-Type": "application/json"},
            json=api_payload
        )
        
        # Parse validation errors
        if response.status_code == 422:
            errors = response.json().get('detail', [])
            error_msgs = [
                f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg', 'Unknown error')}"
                for e in errors if isinstance(e, dict)
            ] if isinstance(errors, list) else []
            raise Exception("Validation errors:\n" + "\n".join(error_msgs) if error_msgs else "Unknown validation error")
            
        response.raise_for_status()
        return response.json()
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise Exception(f"Invalid input: {str(ve)}")
    except requests.exceptions.RequestException as req_exc:
        logger.error(f"API request failed: {str(req_exc)}")
        raise Exception(f"Failed to connect to server: {str(req_exc)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise Exception(f"Could not add inventory item: {str(e)}")
