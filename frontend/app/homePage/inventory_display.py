from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def display_inventory_items(inventory_listbox, items):
    """Display inventory items in Treeview table format with fixed headers"""
    if inventory_listbox:
        for item in inventory_listbox.get_children():
            inventory_listbox.delete(item)
        
        if not items or len(items) == 0:
            empty_values = [''] * 22
            empty_values[11] = 'No inventory items found'
            inventory_listbox.insert('', 'end', values=empty_values, tags=('no_data',))
            inventory_listbox.tag_configure('no_data', foreground='#7f8c8d', font=('Arial', 12, 'italic'))
            return

        for idx, item in enumerate(items, start=1):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            
            values = (
                item.get('ID', item.get('id', '')),
                item.get('Serial No.', item.get('sno', '')),
                item.get('InventoryID', item.get('inventory_id', '')),
                item.get('Product ID', item.get('product_id', '')),
                item.get('Name', item.get('inventory_name', '')),
                item.get('Material', item.get('material', '')),
                item.get('Total Quantity', item.get('total_quantity', '')),
                item.get('Manufacturer', item.get('manufacturer', '')),
                item.get('Purchase Dealer', item.get('purchase_dealer', '')),
                item.get('Purchase Date', item.get('purchase_date', '')),
                item.get('Purchase Amount', item.get('purchase_amount', '')),
                item.get('Repair Quantity', item.get('repair_quantity', '')),
                item.get('Repair Cost', item.get('repair_cost', '')),
                item.get('On Rent', item.get('on_rent', '')),
                item.get('Vendor Name', item.get('vendor_name', '')),
                item.get('Total Rent', item.get('total_rent', '')),
                item.get('Rented Returned', item.get('rented_inventory_returned', '')),
                item.get('Returned Date', item.get('returned_date', '')),
                item.get('On Event', item.get('on_event', '')),
                item.get('In Office', item.get('in_office', '')),
                item.get('In Warehouse', item.get('in_warehouse', '')),
                item.get('Issued Qty', item.get('issued_qty', '')),
                item.get('Balance Qty', item.get('balance_qty', '')),
                item.get('BarCode', item.get('bar_code', item.get('inventory_barcode', ''))),
                item.get('BacodeUrl', item.get('barcode_url', item.get('inventory_barcode_url', ''))),
                item.get('QrCodeUrl', item.get('qrcode_url', item.get('inventory_qrcode_url', ''))),
                item.get('Created At', item.get('created_at', '')),
                item.get('Updated At', item.get('updated_at', '')),
                item.get('Submitted By', item.get('submitted_by', ''))
            )
            
            inventory_listbox.insert('', 'end', values=values, tags=(tag,))
