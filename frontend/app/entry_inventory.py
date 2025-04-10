import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import platform
import uuid
import re
import logging

from .api_request.entry_inventory_api_request import (sync_inventory, 
                            filter_inventory_by_date_range,
                            add_new_inventory_item,
                            search_inventory_by_id
                            )
from .to_event import ToEventWindow
from .from_event import FromEventWindow
from .assign_inventory import AssignInventoryWindow
from .damage_inventory import DamageWindow
import requests
from typing import List, Dict
from .api_request.entry_inventory_api_request import search_project_details_by_project_id

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
search_results_listbox = None
search_inventory_id_entry = None
search_project_id_entry = None
search_product_id_entry = None

# Global variables for entry form
entries = {}
checkbox_vars = {}

def clear_fields():
    """Clear all input fields and reset checkboxes"""
    for entry in entries.values():
        if isinstance(entry, tk.Entry):
            entry.delete(0, tk.END)
    for var in checkbox_vars.values():
        var.set(False)

def update_inventory_list():
    """Update all three listboxes with current data"""
    update_main_inventory_list()
    # Clear added items and search results when refreshing main inventory
    if added_items_listbox:
        added_items_listbox.delete(0, tk.END)
    if search_results_listbox:
        search_results_listbox.delete(0, tk.END)

# Update main inventory listbox with all items by clicking sync button
def update_main_inventory_list():
    """Update only the main inventory listbox with all items"""
    if inventory_listbox:
        inventory_listbox.delete(0, tk.END)
        try:
            inventory = sync_inventory() # This now returns formatted data from the API
            display_inventory_items(inventory)
        except Exception as e:
            logger.error(f"Failed to Sync inventory: {e}")
            messagebox.showerror("Error", "Could not Sync inventory data")

def display_inventory_items(items):
    """Display formatted inventory items in the listbox"""
    if inventory_listbox:
        inventory_listbox.delete(0, tk.END)
        for item in items:
            # Format the display string
            display_str = (
                f"{item['Name']} |{item['Serial No.']} | {item['InventoryID']} | {item['Product ID']} | "
                f"{item['Vendor Name']} | {item['Material']} | {item['Total Quantity']} | "
                f"{item['Manufacturer']} | {item['Purchase Dealer']} | {item['Purchase Date']} | "
                f"{item['Purchase Amount']} | {item['Repair Quantity']} | {item['Repair Cost']} | "
                f"{item['On Rent']} | {item['Total Rent']} | "
                f"{item['Rented Inventory Returned']} | {item['Returned Date']} | {item['On Event']} | "
                f"{item['In Office']} | {item['In Warehouse']} | {item['Issued Qty']} | "
                f"{item['Balance Qty']} | {item['Submitted By']} | {item['ID']} | {item['Created At']} | "
                f"{item['Updated At']} | {item['BarCode']} "
            )
            # Insert the formatted string into the listbox
            inventory_listbox.insert(tk.END, display_str)

#  Filter inventory by date range by `filter` button
def filter_by_date_range():
    """Filter inventory items by date range"""
    from_date_str = from_date_entry.get()
    to_date_str = to_date_entry.get()
    
    if not from_date_str or not to_date_str:
          messagebox.showwarning("Warning", "Please select both From and To dates")
          return
    try:
        # Convert dates to proper format if needed
        from_date_obj = datetime.strptime(from_date_str, "%Y-%m-%d")
        to_date_obj = datetime.strptime(to_date_str, "%Y-%m-%d")
        
        if from_date_obj > to_date_obj:
            messagebox.showwarning("Warning", "From date cannot be after To date")
            return
            
        # Pass the date strings directly
        items = filter_inventory_by_date_range(from_date_str, to_date_str)
        display_inventory_items(items)
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Failed to filter by date range: {e}")
        messagebox.showerror("Error", "Could not filter inventory by date range")

#  Perform inventory search based on search criteria [InventoryID, ProjectID, ProductID]
def perform_search():
    """Perform inventory search based on search criteria"""
    inventory_id = search_inventory_id_entry.get().strip()
    project_id = search_project_id_entry.get().strip()
    product_id = search_product_id_entry.get().strip()
    
    search_results_listbox.delete(0, tk.END)
    
    try:
        if project_id:
            results = search_project_details_by_project_id(project_id)
            if not results:
                messagebox.showinfo("Search Results", "No matching project found")
                return
                
            project = results[0]
            header = (
                f"Project: {project.get('project_name', 'N/A')} | "
                f"ID: {project.get('work_id', 'N/A')}\n"
                f"Employee: {project.get('employee_name', 'N/A')} | "
                f"Client: {project.get('client_name', 'N/A')}\n"
                f"Location: {project.get('location', 'N/A')} | "
                f"Setup Date: {project.get('setup_date', 'N/A')} | "
                f"Event Date: {project.get('event_date', 'N/A')}\n"
                f"Submitted: {project.get('submitted_by', 'N/A')} | "
                f"Updated: {project.get('updated_at', 'N/A')}"
            )
            search_results_listbox.insert(tk.END, header)
            search_results_listbox.insert(tk.END, "-"*80)
            search_results_listbox.insert(tk.END, "Inventory Items:")
            
            for item in project.get('inventory_items', []):
                display_text = (
                    f"{item.get('sno', '')} | "
                    f"{item.get('name', '')} | "
                    f"Qty: {str(item.get('quantity', 0))} | "
                    f"Zone: {item.get('zone_active', '')} | "
                    f"comments: {item.get('comments', '')} | "
                    f"Status: {item.get('status', '')}  |"
                    f"Total: {str(item.get('total', 0))} | "
                    f"Unit: {item.get('unit', '')} | "
                    f"poc: {str(item.get('poc', 0))}"
                )
                search_results_listbox.insert(tk.END, display_text)
                
        elif inventory_id or product_id:
            # Handle inventory/product search
            results = search_inventory_by_id(
                inventory_id=inventory_id,
                product_id=product_id
            )
            
            if not results:
                messagebox.showinfo("Search Results", "No matching items found")
                return
                
            # Display inventory results
            for item in results:
                display_text = (
                    f"{item.get('Sno', '')} | {item.get('InventoryID', 'N/A')} | "
                    f"{item.get('Product ID', 'N/A')} | {item.get('Name', 'N/A')} | "
                    f"Qty: {item.get('Qty', 0)} | Purchase: {item.get('Purchase Date', 'N/A')}"
                )
                search_results_listbox.insert(tk.END, display_text)
                
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        messagebox.showerror("Search Error", f"Failed to perform search: {str(e)}")

# Add new inventory items from all rows
def create_inventory_item(scrollable_frame, header_labels):
    """Add new inventory items from all rows with all fields optional"""
    row_count = len(scrollable_frame.grid_slaves()) // len(header_labels)
    checkbox_fields = ['OnRent', 'RentedInventoryReturned', 'OnEvent', 'InOffice', 'InWarehouse']
    all_fields = ['InventoryID', 'ProductID', 'Name', 'TotalQuantity', 'Submitedby',
                 'ReturnedDate', 'Material', 'Manufacturer', 'PurchaseDealer',
                 'RepairQuantity', 'RepairCost', 'IssuedQty', 'BalanceQty',
                 'PurchaseDate', 'PurchaseAmount', 'VendorName', 'TotalRent', 'Sno']
    
    added_items = []
    
    for row in range(row_count):
        item_data = {}
        
        # Helper function to safely get and clean field values
        def get_field_value(field_name, default=None):
            if field_name in entries and isinstance(entries[field_name], tk.Entry):
                value = entries[field_name].get()
                return value.strip() if value else None
            return None

        # Collect all field values
        for field in all_fields:
            field_name = f"{field}_{row}" if row > 0 else field
            value = get_field_value(field_name)
            if value is not None:
                item_data[field] = value
        
        # Handle checkboxes
        for field in checkbox_fields:
            field_name = f"{field}_{row}" if row > 0 else field
            if field_name in checkbox_vars:
                item_data[field] = checkbox_vars[field_name].get()
        
        if item_data:
            try:
                added_item = add_new_inventory_item(item_data)
                added_items.append(added_item)
            except Exception as e:
                logger.error(f"Failed to add item (row {row+1}): {str(e)}")
                messagebox.showerror("Error", f"Failed to add item from row {row+1}\nError: {str(e)}")

    # Display results if any items were added
    if added_items:
        if added_items_listbox:
            added_items_listbox.delete(0, tk.END)
            for idx, item in enumerate(added_items, start=1):
                display_str = (
                    f"ID: {idx}. {item.get('uuid', 'N/A')} | "
                    f"Serial No.: {item.get('sno', 'N/A')} | "
                    f"Inventory ID: {item.get('inventory_id', 'N/A')} | "
                    f"Product ID: {item.get('product_id', 'N/A')} | "
                    f"Name: {item.get('name', 'N/A')} | "
                    f"Qty: {item.get('total_quantity', 'N/A')} | "
                    f"On Rent: {item.get('on_rent', 'N/A')} | "
                    f"Returned: {item.get('rented_inventory_returned', 'N/A')} | "
                    f"Balance: {item.get('balance_qty', 'N/A')} | "
                    f"Purchased: {item.get('purchase_date', 'N/A')} | "
                    f"Created At: {item.get('created_at', 'N/A')} | "
                    f"Updated At: {item.get('updated_at', 'N/A')} | "
                    f"submitted_by: {item.get('submitted_by', 'N/A')}"
                    f"BarCode: {item.get('bar_code', 'N/A')} | "
                )
                added_items_listbox.insert(tk.END, display_str)
        
        clear_fields()
        update_main_inventory_list()
        messagebox.showinfo("Success", f"{len(added_items)} items added successfully")
    else:
        messagebox.showwarning("Warning", "No items were added")
        
#  Add a new row of input fields below the existing ones
def add_new_row(scrollable_frame, header_labels):
    """Add a new row of input fields below the existing ones"""
    row_num = len(scrollable_frame.grid_slaves()) // len(header_labels)  # Calculate current row count
    
    for col, field in enumerate(header_labels):
        var_name = f"{field.replace(' ', '')}_{row_num}"  # Unique name for each row
        if field in ['On Rent', 'Rented Inventory Returned', 'On Event', 'In Office', 'In Warehouse']:
            checkbox_vars[var_name] = tk.BooleanVar()
            entries[var_name] = tk.Checkbutton(
                scrollable_frame, 
                variable=checkbox_vars[var_name],
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=row_num, column=col, sticky='ew', padx=1, pady=1)
        else:
            entries[var_name] = tk.Entry(
                scrollable_frame, 
                font=('Helvetica', 9), 
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=row_num, column=col, sticky='ew', padx=1, pady=1)

#  Remove the last row of input fields
def remove_last_row(scrollable_frame):
    """Remove the last row of input fields"""
    # Get all widgets in the scrollable frame
    widgets = scrollable_frame.grid_slaves()
    if not widgets:
        return
    
    # Find the highest row number
    max_row = max(int(w.grid_info()['row']) for w in widgets)
    
    # Remove all widgets in the last row
    for widget in widgets:
        if widget.grid_info()['row'] == max_row:
            widget.destroy()
            # Also remove from entries/checkbox_vars if needed
            for key in list(entries.keys()):
                if key.endswith(f"_{max_row}"):
                    del entries[key]
            for key in list(checkbox_vars.keys()):
                if key.endswith(f"_{max_row}"):
                    del checkbox_vars[key]

def update_clock():
    """Update the clock label with current time"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clock_label.config(text=now)
    root.after(1000, update_clock)

def quit_application():
    """Confirm and quit the application"""
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

#  Adjust UI elements based on screen size
def configure_responsive_grid():
    """Adjust UI elements based on screen size"""
    screen_width = root.winfo_screenwidth()
    font_size = max(6, screen_width // 100)

    clock_label.config(font=('Helvetica', 8))
    company_label.config(font=('Helvetica', 7))

# ==============================
# Child window functions
# ==============================
def open_to_event():
    try:
        logger.info("Opening To Event window")
        ToEventWindow(root)
    except Exception as e:
        logger.error(f"Failed to open To Event window: {e}")
        messagebox.showerror("Error", "Could not open To Event window")

def open_from_event():
    try:
        logger.info("Opening Return From Event window")
        FromEventWindow(root)
    except Exception as e:
        logger.error(f"Failed to open Return From Event window: {e}")
        messagebox.showerror("Error", "Could not open Return From Event window")

def open_assign_inventory():
    try:
        logger.info("Opening Assign Inventory window")
        AssignInventoryWindow(root)
    except Exception as e:
        logger.error(f"Failed to open Assign Inventory window: {e}")
        messagebox.showerror("Error", "Could not open Assign Inventory window")

def open_damage_inventory():
    try:
        logger.info("Opening Damage/Waste/Not Working/Lost window")
        DamageWindow(root)
    except Exception as e:
        logger.error(f"Failed to open Damage/Waste/Not Working/Lost window: {e}")
        messagebox.showerror("Error", "Could not open Damage/Waste/Not Working/Lost window")

# Main application setup
def setup_main_window():
    """Configure the main application window"""
    global root
    root = tk.Tk()
    root.title("Tagglabs's Inventory")

    # Window maximization
    try:
        root.state('zoomed')
    except tk.TclError:
        try:
            if platform.system() == 'Linux':
                root.attributes('-zoomed', True)
            else:
                root.attributes('-fullscreen', True)
        except:
            root.geometry("{0}x{1}+0+0".format(
                root.winfo_screenwidth(),
                root.winfo_screenheight()
            ))

    return root

#  Create and configure the header frame with clock and company info
def create_header_frame(root):
    """Create and configure the header frame with clock and company info"""
    header_frame = tk.Frame(root)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=0)
    
    # Configure grid for header frame
    header_frame.grid_columnconfigure(0, weight=1)
    header_frame.grid_rowconfigure(0, weight=1)
    header_frame.grid_rowconfigure(1, weight=1)
    
    # Row 1: Clock (top-center)
    global clock_label
    clock_label = tk.Label(header_frame, font=('Helvetica', 8))
    clock_label.grid(row=0, column=0, sticky='n', pady=(0,0))
    
    # Row 2: Company info (top-right-corner)
    company_info = """Tagglabs Experiential Pvt. Ltd.
Sector 49, Gurugram, Haryana 122018
201, Second Floor, Eros City Square Mall
Eros City Square
098214 43358"""
    
    global company_label
    company_label = tk.Label(header_frame,
                           text=company_info,
                           font=('Helvetica', 9),
                           justify=tk.RIGHT)
    company_label.grid(row=1, column=0, sticky='ne', pady=(0,5))
    
    return header_frame

#  Create list frames with notebook tabs [Inventory List, New Entry, Search Results]
def create_list_frames(root):
    """Create list frames with notebook tabs"""
    # Calculate 65% of screen height
    screen_height = root.winfo_screenheight()
    list_frame_height = int(screen_height * 0.65)
    listbox_height = max(10, list_frame_height // 30)  # Dynamic row count
    
    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
    
    # Frame 1: Inventory List
    inventory_frame = tk.Frame(notebook)
    notebook.add(inventory_frame, text="Inventory List")
    
    # Date range filter frame (only visible when in Inventory List tab) by clicking `filter` button
    date_filter_frame = tk.Frame(inventory_frame)
    date_filter_frame.pack(fill="x", pady=5)
    
    global from_date_entry, to_date_entry
    
    # Left side controls
    left_frame = tk.Frame(date_filter_frame)
    left_frame.pack(side="left", fill="x", expand=True)
    
    # From Date
    tk.Label(left_frame, text="From Date:", font=('Helvetica', 9)).grid(row=0, column=0, padx=5, sticky='e')
    from_date_entry = tk.Entry(left_frame, font=('Helvetica', 9), width=12)
    from_date_entry.grid(row=0, column=1, padx=5, sticky='w')
    from_date_entry.insert(0, datetime.now().strftime("%Y-%m-01"))
    
    # To Date
    tk.Label(left_frame, text="To Date:", font=('Helvetica', 9)).grid(row=0, column=2, padx=5, sticky='e')
    to_date_entry = tk.Entry(left_frame, font=('Helvetica', 9), width=12)
    to_date_entry.grid(row=0, column=3, padx=5, sticky='w')
    to_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    # Filter button
    filter_btn = tk.Button(left_frame, text="Filter", command=filter_by_date_range,
                         font=('Helvetica', 9, 'bold'))
    filter_btn.grid(row=0, column=4, padx=5)
    
    # Show All button
    show_all_btn = tk.Button(left_frame, text="Show All", command=update_main_inventory_list,
                           font=('Helvetica', 9))
    show_all_btn.grid(row=0, column=5, padx=5)
    
    # Right side controls
    right_frame = tk.Frame(date_filter_frame)
    right_frame.pack(side="right", fill="x")
    
    # Main List Sync Item Container button
    sync_btn = tk.Button(
        right_frame, 
        text="Sync", 
        command=update_inventory_list,  # This should trigger the full refresh
        font=('Helvetica', 9, 'bold')
    )
    sync_btn.pack(side="right", padx=5)
    
    # Separator
    ttk.Separator(inventory_frame, orient='horizontal').pack(fill="x", pady=5)
    
    # Main List Sync Item Container
    list_container = tk.Frame(inventory_frame)
    list_container.pack(fill="both", expand=True)
    
    global inventory_listbox
    inventory_listbox = tk.Listbox(
        list_container,
        height=listbox_height,
        font=('Helvetica', 9),
        activestyle='none',
        selectbackground='#4a6984',
        selectforeground='white'
    )
    inventory_listbox.pack(side="left", fill="both", expand=True)
    
    scrollbar = tk.Scrollbar(
        list_container,
        orient="vertical",
        command=inventory_listbox.yview
    )
    scrollbar.pack(side="right", fill="y")
    inventory_listbox.config(yscrollcommand=scrollbar.set)
    
    # Initialize the inventory list
    update_main_inventory_list()
    
    # Frame 2: New Entry - Updated to match requested layout
    """Create the new entry tab with all its components"""
    new_entry_frame = tk.Frame(notebook)
    notebook.add(new_entry_frame, text="New Entry")
    
    # Main container for the form
    form_container = tk.Frame(new_entry_frame)
    form_container.pack(fill='both', expand=True, padx=10, pady=5)
    
    # Container for the header and input rows with scrollbars
    scroll_container = tk.Frame(form_container)
    scroll_container.pack(fill='both', expand=True)
    
    # Create canvas and scrollbars
    canvas = tk.Canvas(scroll_container)
    h_scrollbar = tk.Scrollbar(scroll_container, orient='horizontal', command=canvas.xview)
    v_scrollbar = tk.Scrollbar(scroll_container, orient='vertical', command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
    
    # Grid layout for canvas and scrollbars
    canvas.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')
    
    # Configure grid weights
    scroll_container.grid_rowconfigure(0, weight=1)
    scroll_container.grid_columnconfigure(0, weight=1)
    
    # Create the entry form inside the scrollable frame
    global entries, checkbox_vars
    entries = {}
    checkbox_vars = {}
    
    # Header row with field names
    header_labels = [
        'Sno', "InventoryID", "ProductID", 'Name', 'Material', 'Total Quantity', 
        'Manufacturer', 'Purchase Dealer', 'Purchase Date', 'Purchase Amount', 
        'Repair Quantity', 'Repair Cost', 'On Rent', 'Vendor Name', 'Total Rent', 
        'Rented Inventory Returned', 'Returned Date', 'On Event', 'In Office', 
        'In Warehouse', 'Issued Qty', 'Balance Qty', 'Submited by'
    ]
    
    # Create header row (i)
    for col, label in enumerate(header_labels):
        header = tk.Label(scrollable_frame, text=label, 
                         font=('Helvetica', 9, 'bold'), borderwidth=1, relief='solid')
        header.grid(row=0, column=col, sticky='ew', padx=1, pady=1)
    
    # Input fields row (ii)
    for col, field in enumerate(header_labels):
        var_name = field.replace(' ', '')
        if field in ['On Rent', 'Rented Inventory Returned', 'On Event', 'In Office', 'In Warehouse']:
            checkbox_vars[var_name] = tk.BooleanVar()
            entries[var_name] = tk.Checkbutton(
                scrollable_frame, 
                variable=checkbox_vars[var_name],
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=1, column=col, sticky='ew', padx=1, pady=1)
        else:
            entries[var_name] = tk.Entry(
                scrollable_frame, 
                font=('Helvetica', 9), 
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=1, column=col, sticky='ew', padx=1, pady=1)
    
    # Configure column weights
    for col in range(len(header_labels)):
        scrollable_frame.grid_columnconfigure(col, weight=1)
    
    # Button container
    button_frame = tk.Frame(form_container)
    button_frame.pack(fill='x', pady=5)
    
    # Remove Row button
    remove_row_button = tk.Button(
        button_frame, 
        text="Remove Row", 
        command=lambda: remove_last_row(scrollable_frame),
        font=('Helvetica', 10, 'bold'),
        width=15
    )
    remove_row_button.pack(side='left', padx=0)
    
    # Add Item button
    add_button = tk.Button(
        button_frame, 
        text="Add Item", 
        command=lambda: create_inventory_item(scrollable_frame, header_labels),
        font=('Helvetica', 10, 'bold'),
        width=15
    )
    add_button.pack(side='left', padx=5, expand=True)
    
    # Add Row button
    add_row_button = tk.Button(
        button_frame, 
        text="Add Row", 
        command=lambda: add_new_row(scrollable_frame, header_labels),
        font=('Helvetica', 10, 'bold'),
        width=15
    )
    add_row_button.pack(side='left', padx=0)
    
    # Added Items List section
    list_frame = tk.Frame(new_entry_frame)
    list_frame.pack(fill='both', expand=True, padx=10, pady=5)
    
    # "Added Items List" label centered
    list_label = tk.Label(
        list_frame, 
        text="Added Items List", 
        font=('Helvetica', 10, 'bold')
    )
    list_label.pack()
    
    # Create container for the listbox with vertical scroll only
    list_container = tk.Frame(list_frame)
    list_container.pack(fill='both', expand=True)
    
    global added_items_listbox
    added_items_listbox = tk.Listbox(
        list_container,
        height=10,
        font=('Helvetica', 9),
        selectbackground='#4a6984',
        selectforeground='white'
    )
    added_items_listbox.pack(side="left", fill="both", expand=True)

    # Add vertical scrollbar
    list_scrollbar = tk.Scrollbar(
        list_container,
        orient="vertical",
        command=added_items_listbox.yview
    )
    list_scrollbar.pack(side="right", fill="y")
    added_items_listbox.config(yscrollcommand=list_scrollbar.set)

    # Frame 3: Search Results
    search_frame = tk.Frame(notebook)
    notebook.add(search_frame, text="Search Results")
    
    # Search fields
    search_fields_frame = tk.Frame(search_frame)
    search_fields_frame.pack(fill="x", pady=5)
    
    global search_inventory_id_entry, search_project_id_entry, search_product_id_entry
    
    tk.Label(search_fields_frame, text="Inventory ID:", font=('Helvetica', 9)).grid(row=0, column=0, sticky='e', padx=5)
    search_inventory_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 9), width=20)
    search_inventory_id_entry.grid(row=0, column=1, sticky='w', padx=5)
    
    tk.Label(search_fields_frame, text="Project ID:", font=('Helvetica', 9)).grid(row=0, column=2, sticky='e', padx=5)
    search_project_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 9), width=20)
    search_project_id_entry.grid(row=0, column=3, sticky='w', padx=5)
    
    tk.Label(search_fields_frame, text="Product ID:", font=('Helvetica', 9)).grid(row=0, column=4, sticky='e', padx=5)
    search_product_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 9), width=20)
    search_product_id_entry.grid(row=0, column=5, sticky='w', padx=5)

    # Search button
    search_btn = tk.Button(search_fields_frame, text="Search", command=perform_search, 
                         font=('Helvetica', 9, 'bold'))
    search_btn.grid(row=0, column=6, sticky='e', padx=5)

    # Separator line
    ttk.Separator(search_frame, orient='horizontal').pack(fill="x", pady=5)
    
    # Search Results list container
    search_list_container = tk.Frame(search_frame)
    search_list_container.pack(fill="both", expand=True)
    
    global search_results_listbox
    search_results_listbox = tk.Listbox(
        search_list_container,
        height=listbox_height,
        font=('Helvetica', 9),
        activestyle='none',
        selectbackground='#4a6984',
        selectforeground='white'
    )
    search_results_listbox.pack(side="left", fill="both", expand=True)
    
    search_scrollbar = tk.Scrollbar(
        search_list_container,
        orient="vertical",
        command=search_results_listbox.yview
    )
    search_scrollbar.pack(side="right", fill="y")
    search_results_listbox.config(yscrollcommand=search_scrollbar.set)
    
    return notebook

def create_bottom_frames(root):
    """Create the bottom frames with action buttons"""
    # Bottom-left buttons
    bottom_left_frame = tk.Frame(root)
    bottom_left_frame.grid(row=2, column=0, sticky='sw', padx=10, pady=10)
    
    buttons = [
        ("To Event", open_to_event),
        ("From Event", open_from_event),
        ("Assigned", open_assign_inventory),
        ("Damage/Waste/Not Working", open_damage_inventory)
    ]
    
    for text, command in buttons:
        btn = tk.Button(
            bottom_left_frame,
            text=text,
            command=command,
            font=('Helvetica', 9, 'bold'),
            width=30
        )
        btn.pack(side='left', padx=5)
    
    # Quit button
    quit_frame = tk.Frame(root)
    quit_frame.grid(row=2, column=1, sticky='se', padx=10, pady=10)
    
    quit_button = tk.Button(quit_frame, text="Quit", command=quit_application,
                          font=('Helvetica', 10, 'bold'), width=10)
    quit_button.pack()

def configure_grid(root):
    """Configure the root grid layout"""
    root.grid_rowconfigure(0, weight=0)  # Header
    root.grid_rowconfigure(1, weight=1)  # List frames
    root.grid_rowconfigure(2, weight=0)  # Bottom buttons
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

def main():
    """Main application entry point"""
    global root
    root = setup_main_window()
    
    # Create frames in order
    header_frame = create_header_frame(root)  # Row 0: Clock and company info
    notebook = create_list_frames(root)      # Row 1: Display lists (includes initial update)
    create_bottom_frames(root)               # Row 2: Bottom buttons
    
    configure_grid(root)
    
    # Initialize other components
    configure_responsive_grid()
    root.bind('<Configure>', lambda e: configure_responsive_grid())
    update_clock()

    root.protocol("WM_DELETE_WINDOW", quit_application)
    
    root.mainloop()

if __name__ == "__main__":
    main()