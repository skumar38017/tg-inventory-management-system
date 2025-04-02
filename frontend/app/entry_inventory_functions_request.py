#  frontend/app/entry_inventory_functions_request.py
import requests
from typing import List, Dict
import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)

#  Sync inventory data from the API by `sync` button
def sync_inventory() -> List[Dict]:
    """Fetch inventory data from the API and return formatted data"""
    try:
        response = requests.get("http://localhost:8000/api/v1/sync/")
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
                # Add any other fields you want to display
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch inventory: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data")
        return []

#  Filter inventory by date range by `filter` button
def filter_inventory_by_date_range(from_date, to_date) -> List[Dict]:
    """Fetch inventory data filtered by date range from the API and return formatted data"""
    try:
        # Get the date strings from the Tkinter StringVars
        from_date_str = from_date.get()
        to_date_str = to_date.get()
        
        # Make the API request
        response = requests.get(
            "http://localhost:8000/api/v1/date-range/",
            params={
                "from_date": from_date_str,
                "to_date": to_date_str
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
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch inventory by date range: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data by date range")
        return []