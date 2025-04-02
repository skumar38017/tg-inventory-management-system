#  frontend/app/entry_inventory_functions_request.py
import requests
from typing import List, Dict
import logging
from tkinter import messagebox
from datetime import datetime, timezone, date

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
                'BarCode': item.get('barcode', 'N/A'),
                # Add any other fields you want to display
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch inventory: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data")
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
                'BarCode': item.get('barcode', 'N/A'),
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch inventory by date range: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data by date range")
        return []
    
#  Add new inventory items to the database by clicking the `Add Item` button
def add_new_inventory_item(item_data: dict):
    """Add new inventory items to the database"""
    try:
        # Map UI field names to API field names
        api_payload = {
            "product_id": item_data.get('ProductID', ''),
            "inventory_id": item_data.get('InventoryID', ''),
            "sno": item_data.get('SNo', ''),
            "name": item_data.get('Name', ''),
            "material": item_data.get('Material', ''),
            "total_quantity": str(item_data.get('TotalQuantity', '')),
            "manufacturer": item_data.get('Manufacturer', ''),
            "purchase_dealer": item_data.get('PurchaseDealer', ''),
            "purchase_date": item_data.get('PurchaseDate', datetime.now().date().isoformat()),
            "purchase_amount": str(item_data.get('PurchaseAmount', '')),
            "repair_quantity": str(item_data.get('RepairQuantity', '')),
            "repair_cost": str(item_data.get('RepairCost', '')),
            "on_rent": str(item_data.get('OnRent', False)).lower(),
            "vendor_name": item_data.get('VendorName', ''),
            "total_rent": str(item_data.get('TotalRent', '')),
            "rented_inventory_returned": str(item_data.get('RentedInventoryReturned', False)).lower(),
            "returned_date": item_data.get('ReturnedDate', ''),
            "on_event": str(item_data.get('OnEvent', False)).lower(),
            "in_office": str(item_data.get('InOffice', False)).lower(),
            "in_warehouse": str(item_data.get('InWarehouse', False)).lower(),
            "issued_qty": str(item_data.get('IssuedQty', '')),
            "balance_qty": str(item_data.get('BalanceQty', '')),
            "submitted_by": item_data.get('Submitedby', ''),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        # Remove empty optional fields
        api_payload = {k: v for k, v in api_payload.items() if v not in ['', None]}

        # Post the new inventory item to the database
        response = requests.post(
            url="http://localhost:8000/api/v1/create-item/",
            headers={"Content-Type": "application/json"},
            json=api_payload
        )
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        logger.error(f"Failed to add new inventory item: {e}")
        raise Exception("Could not add new inventory item")