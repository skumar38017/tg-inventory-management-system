#  frontend/app/homePage/entry_inventory.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common_imports import *
from utils.pagination import Pagination
from api_request.entry_inventory_api_request import (
    sync_inventory,
    upload_inventory,
    show_all_inventory,
    filter_inventory_by_date_range,
    get_current_page
)
from to_event import ToEventWindow
from from_event import FromEventWindow
from assignPage.assign_inventory import AssignInventoryWindow
from damagePage.damage_inventory import DamageWindow
from homePage.entry_update_pop_window import *
from homePage.reveal_qr_barcode_window import *
from homePage.new_entry import create_new_entry_tab
from homePage.entry_update_pop_window import UpdatePopUpWindow
from homePage.search_results import SearchResults
from homePage.header import create_header_frame
from homePage.pagination import create_pagination_frame
from homePage.bottom_buttons import create_bottom_frames
from homePage.inventory_display import display_inventory_items
from homePage.inventory_list_tab import create_inventory_list_tab

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)
root = None

# Global variables for the listboxes
inventory_listbox = None
added_items_listbox = None

# Global pagination instance
paginator = Pagination()

# Global variables for pagination UI
page_info_label_ref = {}
page_entry_ref = {}

# Global variables for date entries
from_date_entry_ref = {}
to_date_entry_ref = {}

# Global variables for header
clock_label = None
company_label = None

# Global variables for entry form
entries = {}
checkbox_vars = {}

def update_inventory_list():
    """Update all three listboxes with current data"""
    sync_inventory()
    update_main_inventory_list()
    
    # Don't clear today's added items
    today = datetime.now().date()
    current_list_date = getattr(added_items_listbox, 'current_date', None)
    if current_list_date != today:
        if added_items_listbox:
            added_items_listbox.delete(0, tk.END)
            added_items_listbox.current_date = today
        
def update_main_inventory_list():
    """Update only the main inventory listbox with paginated items"""
    if inventory_listbox:
        for item in inventory_listbox.get_children():
            inventory_listbox.delete(item)
        try:
            inventory = show_all_inventory()
            display_inventory_items(inventory_listbox, inventory)
            update_pagination_info()
        except Exception as e:
            logger.error(f"Failed to Sync inventory: {e}")
            custom_messagebox("error", "Error", "Could not Sync inventory data")

def update_pagination_info():
    """Update pagination display info"""
    current_page = get_current_page()
    logger.info(f"Current page: {current_page}")

def go_next_page():
    """Go to next page and refresh data from API"""
    global paginator
    paginator.next_page()
    update_main_inventory_list()  # This hits the API

def go_prev_page():
    """Go to previous page and refresh data from API"""
    global paginator
    paginator.prev_page()
    update_main_inventory_list()  # This hits the API

def go_specific_page(page_num):
    """Go to specific page and refresh data from API"""
    global paginator
    paginator.go_to_page(page_num)
    update_main_inventory_list()  # This hits the API

def go_to_first_page():
    """Go to first page and refresh data from API"""
    global paginator
    paginator.go_to_page(0)
    update_main_inventory_list()

def go_to_page_from_entry():
    """Go to page number from entry field"""
    global paginator
    try:
        page_num = int(page_entry_ref['entry'].get())
        if page_num >= 0:
            paginator.go_to_page(page_num)
            update_main_inventory_list()
    except ValueError:
        custom_messagebox("warning", "Invalid Page", "Please enter a valid page number")

def update_pagination_ui():
    """Update pagination UI elements"""
    global paginator
    if 'label' in page_info_label_ref:
        current_page = paginator.current_page
        page_info_label_ref['label'].config(text=f"Page {current_page} | 20 items per page")
    
    if 'entry' in page_entry_ref:
        page_entry_ref['entry'].delete(0, tk.END)
        page_entry_ref['entry'].insert(0, str(paginator.current_page))

def display_inventory_items(items):
    """Display inventory items in Treeview table format with fixed headers"""
    if inventory_listbox:
        # Clear existing items
        for item in inventory_listbox.get_children():
            inventory_listbox.delete(item)
        
        if not items or len(items) == 0:
            # Insert a centered message when no items found
            empty_values = [''] * 22  # Create empty values for all columns
            empty_values[11] = 'No inventory items found'  # Put message in middle column
            inventory_listbox.insert('', 'end', values=empty_values, tags=('no_data',))
            
            # Configure the no_data tag for better visibility
            inventory_listbox.tag_configure('no_data', foreground='#7f8c8d', font=('Arial', 12, 'italic'))
            return

        # Add each item as a row in the treeview
        for idx, item in enumerate(items, start=1):
            # Determine row tag for alternating colors
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            
            # Extract values for each column
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
            
            # Insert row into treeview
            inventory_listbox.insert('', 'end', values=values, tags=(tag,))
            
def filter_by_date_range():
    """Filter inventory items by date range"""
    from_date_str = from_date_entry_ref['entry'].get()
    to_date_str = to_date_entry_ref['entry'].get()
    
    if not from_date_str or not to_date_str:
          custom_messagebox("warning", "Warning", "Please select both From and To dates")
          return
    try:
        from_date_obj = datetime.strptime(from_date_str, "%Y-%m-%d")
        to_date_obj = datetime.strptime(to_date_str, "%Y-%m-%d")
        
        if from_date_obj > to_date_obj:
            custom_messagebox("warning", "Warning", "From date cannot be after To date")
            return
            
        items = filter_inventory_by_date_range(from_date_str, to_date_str)
        display_inventory_items(inventory_listbox, items)
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        custom_messagebox("error", "Error", "Invalid date format. Please use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Failed to filter by date range: {e}")
        custom_messagebox("error", "Error", "Could not filter inventory by date range")

def quit_application():
    """Confirm and quit the application"""
    if custom_confirmation("Quit", "Do you really want to quit?"):
        root.destroy()

def upload_inventory_with_message():
    """Upload inventory and show success message"""
    result = upload_inventory()
    if result:
        custom_messagebox("info", "Success", "Inventory data uploaded successfully!")
def configure_responsive_grid():
    """Adjust UI elements based on screen size"""
    if clock_label:
        clock_label.config(font=(universal_font_box_size.qr_barcode_header_font_family, 14, 'bold'))
    if company_label:
        company_label.config(font=(universal_font_box_size.qr_barcode_header_font_family, 12))

# ==============================
# Child window functions
# ==============================
def open_to_event():
    try:
        logger.info("Opening To Event window")
        ToEventWindow(root)
    except Exception as e:
        logger.error(f"Failed to open To Event window: {e}")
        custom_messagebox("error", "Error", "Could not open To Event window")

def open_from_event():
    try:
        logger.info("Opening Return From Event window")
        FromEventWindow(root)
    except Exception as e:
        logger.error(f"Failed to open Return From Event window: {e}")
        custom_messagebox("error", "Error", "Could not open Return From Event window")

def open_assign_inventory():
    try:
        logger.info("Opening Assign Inventory window")
        AssignInventoryWindow(root)
    except Exception as e:
        logger.error(f"Failed to open Assign Inventory window: {e}")
        custom_messagebox("error", "Error", "Could not open Assign Inventory window")

def open_damage_inventory():
    try:
        logger.info("Opening Damage/Waste/Not Working/Lost window")
        DamageWindow(root)
    except Exception as e:
        logger.error(f"Failed to open Damage/Waste/Not Working/Lost window: {e}")
        custom_messagebox("error", "Error", "Could not open Damage/Waste/Not Working/Lost window")

# Main application setup
def setup_main_window():
    """Configure the main application window"""
    global root
    root = tk.Tk()
    root.title("Tagglabs Inventory Management System")
    root.configure(bg='#f0f0f0')  # Light gray background
    
    # Configure global messagebox font for consistent appearance across all dialogs
    root.option_add('*Dialog.msg.font', ('Arial', 12))
    
    # Use the imported maximize_window function
    maximize_window(root)
    
    return root

def open_reveal_window():
    """Open the Reveal QR & Barcode window"""
    RevealQrAndBarcodeWindow(root).open_reveal_qr_and_barcode_pop_up()

def create_list_frames(root):
    """Create list frames with notebook tabs"""
    global inventory_listbox
    
    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, sticky="nsew", padx=3, pady=2)
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
    style.configure('TNotebook.Tab', 
                   padding=[20, 12], 
                   font=(universal_font_box_size.qr_barcode_header_font_family, 11, 'bold'),
                   background='#bdc3c7',
                   foreground='#2c3e50')
    style.map('TNotebook.Tab',
             background=[('selected', '#3498db'), ('active', '#5dade2')],
             foreground=[('selected', 'white'), ('active', 'white')])
    
    inventory_listbox_ref = {}
    create_inventory_list_tab(notebook, inventory_listbox_ref, from_date_entry_ref, to_date_entry_ref,
                               filter_by_date_range, update_main_inventory_list, 
                               upload_inventory_with_message, update_inventory_list, root)
    
    inventory_listbox = inventory_listbox_ref['listbox']
    
    update_main_inventory_list()
    
    create_new_entry_tab(notebook)
    
    search_results = SearchResults(root)
    search_results.create_search_results_tab(notebook)
    
    return notebook

def configure_grid(root):
    """Configure the root grid layout"""
    root.grid_rowconfigure(0, weight=0)  # Header
    root.grid_rowconfigure(1, weight=1)  # List frames
    root.grid_rowconfigure(2, weight=0)  # Pagination
    root.grid_rowconfigure(3, weight=0)  # Bottom buttons
    root.grid_columnconfigure(0, weight=1)  # Single column for full width

def main():
    """Main application entry point"""
    global root, clock_label, company_label
    root = setup_main_window()
    
    header_frame, clock_label, company_label = create_header_frame(root)
    notebook = create_list_frames(root)
    create_pagination_frame(root, page_info_label_ref, page_entry_ref, 
                           go_to_first_page, go_prev_page, go_next_page, go_to_page_from_entry)
    create_bottom_frames(root, open_to_event, open_from_event, open_assign_inventory, 
                        open_damage_inventory, quit_application)
    
    configure_grid(root)
    configure_responsive_grid()
    root.bind('<Configure>', lambda e: configure_responsive_grid())
    setup_clock_update(root, clock_label)
    setup_window_closing(root)

    root.mainloop()

if __name__ == "__main__":
    main()