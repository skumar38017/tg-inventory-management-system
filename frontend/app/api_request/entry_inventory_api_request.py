#  frontend/app/entry_inventory_functions_request.py
import requests
from typing import List, Dict
import logging
import tkinter as tk
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
                'BacodeUrl': item.get('barcode_image_url', 'N/A'),
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
                'BacodeUrl': item.get('barcode_image_url', 'N/A'),
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
                'BacodeUrl': item.get('barcode_image_url', 'N/A'),
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch inventory by date range: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data by date range")
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
            "name": clean_value(item_data.get('Name')),
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
        response = requests.post(
            url="http://localhost:8000/api/v1/create-item/",
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
def search_inventory_by_id(inventory_id: str = None, product_id: str = None, project_id: str = None) -> List[Dict]:
    """Fetch inventory data filtered by a single ID from the API"""
    try:
        # Validate that exactly one ID is provided
        provided_ids = [id for id in [inventory_id, product_id, project_id] if id]
        if len(provided_ids) != 1:
            raise ValueError("Please provide exactly one ID (Inventory ID, Product ID, or Project ID) for searching")
        
        # Prepare query parameters
        params = {}
        if inventory_id:
            params['inventory_id'] = inventory_id
        elif product_id:
            params['product_id'] = product_id
        else:
            params['project_id'] = project_id

        # Make the API request with the parameter
        response = requests.get(
            "http://localhost:8000/api/v1/search/",
            params=params
        )
        response.raise_for_status()
        
        # Map backend fields to frontend display names
        formatted_data = []
        for item in response.json():
            formatted_item = {
                'Sno': item.get('sno', 'N/A'),
                'InventoryID': item.get('inventory_id', 'N/A'),
                'Product ID': item.get('product_id', 'N/A'),
                'Name': item.get('name', 'N/A'),
                'Material': item.get('material', 'N/A'),
                'Qty': item.get('total_quantity', 'N/A'),
                'Manufacturer': item.get('manufacturer', 'N/A'),
                'Purchase Dealer': item.get('purchase_dealer', 'N/A'),
                'Purchase Date': item.get('purchase_date', 'N/A'),
                'Purchase Amount': item.get('purchase_amount', 'N/A'),
                'Repair Quantity': item.get('repair_quantity', 'N/A'),
                'Repair Cost': item.get('repair_cost', 'N/A'),
                'On Rent': 'Yes' if item.get('on_rent') else 'No',
                'Vendor Name': item.get('vendor_name', 'N/A'),
                'Total Rent': item.get('total_rent', 'N/A'),
                'Rented Inventory Returned': 'Yes' if item.get('rented_inventory_returned') else 'No',
                'Returned Date': item.get('returned_date', 'N/A'),
                'On Event': 'Yes' if item.get('on_event') else 'No',
                'In Office': 'Yes' if item.get('in_office') else 'No',
                'In Warehouse': 'Yes' if item.get('in_warehouse') else 'No',
                'Issued Qty': item.get('issued_qty', 'N/A'),
                'Balance Qty': item.get('balance_qty', 'N/A'),
                'Submitted By': item.get('submitted_by', 'N/A'),
                'Created At': item.get('created_at', 'N/A'),
                'Updated At': item.get('updated_at', 'N/A'),
                'BarCode': item.get('bar_code', 'N/A'),
                'BacodeUrl': item.get('barcode_image_url', 'N/A'),
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