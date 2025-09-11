#  frontend/app/entry_inventory.py
from common_imports import *
from api_request.entry_inventory_api_request import (
    sync_inventory,
    upload_inventory,
    show_all_inventory,
    filter_inventory_by_date_range,
    add_new_inventory_item,
    search_inventory_by_id,
    update_existing_inventory
)
from api_request.to_event_inventory_request import search_project_details_by_id
from to_event import ToEventWindow
from from_event import FromEventWindow
from assign_inventory import AssignInventoryWindow
from damage_inventory import DamageWindow
from entry_update_pop_window import *
from reveal_qr_barcode_window import *
from homePage.new_entry import create_new_entry_tab
# from .api_request.entry_inventory_api_request import search_project_details_by_project_id

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

def refresh_form(scrollable_frame, header_labels):
    """Refresh the form by clearing fields and regenerating IDs"""
    clear_fields()
    # Re-generate IDs for the first row
    entries['InventoryID'].config(state='normal')
    entries['InventoryID'].delete(0, tk.END)
    entries['InventoryID'].insert(0, generate_inventory_id())
    entries['InventoryID'].config(state='readonly')
    
    entries['ProductID'].config(state='normal')
    entries['ProductID'].delete(0, tk.END)
    entries['ProductID'].insert(0, generate_product_id())
    entries['ProductID'].config(state='readonly')
    
    # Don't clear the added items list if it's from today
    today = datetime.now().date()
    current_list_date = getattr(added_items_listbox, 'current_date', None)
    if current_list_date != today:
        if added_items_listbox:
            added_items_listbox.delete(0, tk.END)
            added_items_listbox.current_date = today
    
    messagebox.showinfo("Refreshed", "Form has been refreshed with new IDs")

def clear_fields():
    """Clear all input fields except InventoryID and ProductID, and reset checkboxes"""
    for field_name, entry in entries.items():
        if isinstance(entry, tk.Entry):
            # Skip InventoryID and ProductID fields
            if field_name.startswith('InventoryID') or field_name.startswith('ProductID'):
                continue
                
            # Temporarily make writable to clear, then restore state if needed
            current_state = entry['state']
            if current_state == 'readonly':
                entry.config(state='normal')
            
            entry.delete(0, tk.END)
            
            if current_state == 'readonly':
                entry.config(state='readonly')
    
    # Reset all checkboxes
    for var in checkbox_vars.values():
        var.set(False)

def update_inventory_list():
    """Update all three listboxes with current data"""
    sync_inventory()
    update_main_inventory_list()
    # Only clear search results when refreshing main inventory
    if search_results_listbox:
        search_results_listbox.delete(0, tk.END)
    
    # Don't clear today's added items
    today = datetime.now().date()
    current_list_date = getattr(added_items_listbox, 'current_date', None)
    if current_list_date != today:
        if added_items_listbox:
            added_items_listbox.delete(0, tk.END)
            added_items_listbox.current_date = today
        
# Update main inventory listbox with all items by clicking sync button
def update_main_inventory_list():
    """Update only the main inventory listbox with all items"""
    if inventory_listbox:
        inventory_listbox.delete(0, tk.END)
        try:
            inventory = show_all_inventory() # This now returns formatted data from the API
            display_inventory_items(inventory)
        except Exception as e:
            logger.error(f"Failed to Sync inventory: {e}")
            messagebox.showerror("Error", "Could not Sync inventory data")

def display_inventory_items(items):
    """Display inventory items in a horizontal table format with fixed headers"""
    if inventory_listbox:
        inventory_listbox.delete(0, tk.END)
        
        if not items:
            inventory_listbox.insert(tk.END, "No inventory items found")
            return

        # Define the column headers and their display widths
        headers = [
            ("ID", 50),
            ("Serial No.", 30),
            ("InventoryID", 20),
            ("Product ID", 20),
            ("Name", 50),
            ("Material", 40),
            ("Total Quantity", 25),
            ("Manufacturer", 40),
            ("Purchase Dealer", 40),
            ("Purchase Date", 35),
            ("Purchase Amount", 25),
            ("Repair Quantity", 25),
            ("Repair Cost", 25),
            ("On Rent", 30),
            ("Vendor Name", 40),
            ("Total Rent", 30),
            ("Rented Inventory Returned", 30),
            ("Returned Date", 30),
            ("On Event", 30),
            ("In Office", 30),
            ("In Warehouse", 35),
            ("Issued Qty", 25),
            ("Balance Qty", 25),
            ("Submitted By", 35),
            ("Created At", 40),
            ("Updated At", 40),
            ("BarCode", 40),
            ("BacodeUrl", 150)
        ]

        # Calculate total width needed
        total_width = sum(h[1] for h in headers)
        
        # Create header row
        header_row = "".join(f"{h[0]:<{h[1]}}" for h in headers)
        inventory_listbox.insert(tk.END, header_row)
        
        # Add separator line
        separator = "-" * total_width
        inventory_listbox.insert(tk.END, separator)
        
        # Add each item's values in a row
        for item in items:
            row_values = []
            for h in headers:
                # Get the value directly using the same keys as in the API response
                value = item.get(h[0], 'N/A')
                
                # Format the value to fit the column width
                display_value = str(value)[:h[1]-2] + ".." if len(str(value)) > h[1] else str(value)
                row_values.append(f"{display_value:<{h[1]}}")
            
            # Join all values with no extra spaces between columns
            inventory_listbox.insert(tk.END, "".join(row_values))
        
        # Configure horizontal scrolling
        inventory_listbox.config(width=total_width)
            
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

# Perform inventory search based on search criteria [InventoryID, 'ProjectID', ProductID]
def perform_search():
    """Perform inventory search based on search criteria and display results in table format"""
    inventory_id = search_inventory_id_entry.get().strip()
    project_id = search_project_id_entry.get().strip()
    product_id = search_product_id_entry.get().strip()
    
    search_results_listbox.delete(0, tk.END)
    
    try:
        if project_id:
            # Project search remains the same but with empty string instead of N/A
            results = search_project_details_by_id(project_id)
            if not results:
                messagebox.showinfo("Search Results", "No matching project found")
                return
                
            project = results[0]
            # Enhanced header with more project details
            header = (
                f"Project: {project.get('project_name', '')} | "
                f"Project_ID: {project.get('work_id', '')} | "
                f"Employee: {project.get('employee_name', '')} | "
                f"Client: {project.get('client_name', '')} | "
                f"Location: {project.get('location', '')}\n"
                f"Setup Date: {project.get('setup_date', '')} | "
                f"Event Date: {project.get('event_date', '')}\n"
                f"Submitted By: {project.get('submitted_by', '')} | "
                f"Created At: {project.get('created_at', '')} | "
                f"Updated At: {project.get('updated_at', '')}"
                f"Barcode: {project.get('barcode', '')}\n"
            )
            search_results_listbox.insert(tk.END, header)
            search_results_listbox.insert(tk.END, "-"*125)
            search_results_listbox.insert(tk.END, "Inventory Items:")
            
            # Define inventory item headers
            item_headers = [
                ("S.No", 30),
                ("Name", 50),
                ("Description", 50),
                ("Qty", 16),
                ("Zone", 35),
                ("Material", 40),
                ("Comments", 50),
                ("Total", 16),
                ("Unit", 16),
                ("Per Unit Power", 25),
                ("Total Power", 25),
                ("Status", 25),
                ("POC", 40),
                ("Item ID", 40)
            ]
            
            # Create header row for inventory items
            header_row = "".join(f"{h[0]:<{h[1]}}" for h in item_headers)
            search_results_listbox.insert(tk.END, header_row)
            
            # Add separator line
            separator = "-" * sum(h[1] for h in item_headers)
            search_results_listbox.insert(tk.END, separator)
            
            # Display each inventory item with proper None handling
            for item in project.get('inventory_items', []):
                # Safe getter function that handles None values
                def safe_get(key, default=''):
                    val = item.get(key, default)
                    return str(val) if val is not None else default
                
                row_values = [
                    safe_get('sno')[:7],
                    safe_get('name')[:18],
                    safe_get('description')[:23],
                    safe_get('quantity')[:4],
                    safe_get('zone_active')[:12],
                    safe_get('material')[:13],
                    safe_get('comments')[:18],
                    safe_get('total')[:6],
                    safe_get('unit')[:6],
                    safe_get('per_unit_power')[:13],
                    safe_get('total_power')[:12],
                    safe_get('status')[:12],
                    safe_get('poc')[:13],
                    safe_get('id')[:36]
                ]
                
                # Format the row
                row = ""
                for i, value in enumerate(row_values):
                    row += f"{value:<{item_headers[i][1]}}"
                
                search_results_listbox.insert(tk.END, row)
                
            # Configure horizontal scrolling based on inventory items width
            search_results_listbox.config(width=sum(h[1] for h in item_headers))
                
        elif inventory_id or product_id:
            # Handle inventory/product search with table format (existing code)
            results = search_inventory_by_id(
                inventory_id=inventory_id,
                product_id=product_id
            )
            
            if not results:
                messagebox.showinfo("Search Results", "No matching items found")
                return
                
            # Define the column headers and their display widths
            headers = [
                ("ID", 50),
                ("Serial No.", 30),
                ("InventoryID", 20),
                ("Product ID", 20),
                ("Name", 50),
                ("Material", 40),
                ("Total Quantity", 25),
                ("Manufacturer", 40),
                ("Purchase Dealer", 40),
                ("Purchase Date", 35),
                ("Purchase Amount", 25),
                ("Repair Quantity", 25),
                ("Repair Cost", 25),
                ("On Rent", 30),
                ("Vendor Name", 40),
                ("Total Rent", 25),
                ("Rented Inventory Returned", 30),
                ("Returned Date", 30),
                ("On Event", 25),
                ("In Office", 30),
                ("In Warehouse", 35),
                ("Issued Qty", 25),
                ("Balance Qty", 25),
                ("Submitted By", 35),
                ("Created At", 40),
                ("Updated At", 40),
                ("BarCode", 40),
                ("BacodeUrl", 150)
            ]

            # Calculate total width needed
            total_width = sum(h[1] for h in headers)
            
            # Create header row
            header_row = "".join(f"{h[0]:<{h[1]}}" for h in headers)
            search_results_listbox.insert(tk.END, header_row)
            
            # Add separator line
            separator = "-" * total_width
            search_results_listbox.insert(tk.END, separator)
            
            # Add each item's values in a row
            for item in results:
                row_values = []
                for h in headers:
                    # Get the value using the exact header text (spaces included)
                    value = item.get(h[0], '')
                    
                    # Format the value to fit the column width
                    display_value = str(value)[:h[1]-2] + ".." if len(str(value)) > h[1] else str(value)
                    row_values.append(f"{display_value:<{h[1]}}")
                
                # Join all values with no extra spaces between columns
                search_results_listbox.insert(tk.END, "".join(row_values))
            
            # Configure horizontal scrolling
            search_results_listbox.config(width=total_width)
                
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
    today = datetime.now().date()
    
    # Track if we have any valid data to submit
    has_valid_data = False
    
    for row in range(row_count):
        item_data = {}
        row_has_data = False
        
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
            if value:
                item_data[field] = value
                row_has_data = True
        
        # Skip empty rows (except first row which is required)
        if not row_has_data and row > 0:
            continue
            
        has_valid_data = has_valid_data or row_has_data
        
        # Auto-generate InventoryID if not provided
        if 'InventoryID' not in item_data or not item_data['InventoryID']:
            item_data['InventoryID'] = generate_inventory_id()
        
        # Auto-generate ProductID if not provided
        if 'ProductID' not in item_data or not item_data['ProductID']:
            item_data['ProductID'] = generate_product_id()
        
        # Handle checkboxes
        for field in checkbox_fields:
            field_name = f"{field}_{row}" if row > 0 else field
            if field_name in checkbox_vars:
                item_data[field] = checkbox_vars[field_name].get()
                if item_data[field]:  # If checkbox is checked
                    row_has_data = True
        
        if row_has_data or row == 0:  # Always process first row
            try:
                # Add current date to the item data
                item_data['added_date'] = today.strftime("%Y-%m-%d")
                added_item = add_new_inventory_item(item_data)
                added_items.append(added_item)
            except Exception as e:
                logger.error(f"Failed to add item (row {row+1}): {str(e)}")
                messagebox.showerror("Error", f"Failed to add item from row {row+1}\nError: {str(e)}")
                return  # Stop processing if there's an error

    if not has_valid_data and row_count > 1:
        messagebox.showwarning("Warning", "No valid data to submit in additional rows")
        return

    # Display results if any items were added
    if added_items:
        if added_items_listbox:
            # Only clear if we're starting a new day
            current_list_date = getattr(added_items_listbox, 'current_date', None)
            if current_list_date != today:
                added_items_listbox.delete(0, tk.END)
                added_items_listbox.current_date = today
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for idx, item in enumerate(added_items, start=1):
                display_str = (
                    f"[Today] ID: {idx}. {item.get('id', 'N/A')} | "
                    f"Serial No.: {item.get('sno', 'N/A')} | "
                    f"Inventory ID: {item.get('inventory_id', 'N/A')} | "
                    f"Product ID: {item.get('product_id', 'N/A')} | "
                    f"Name: {item.get('inventory_name', 'N/A')} | "
                    f"Qty: {item.get('total_quantity', 'N/A')} | "
                    f"On Rent: {item.get('on_rent', 'N/A')} | "
                    f"Returned: {item.get('rented_inventory_returned', 'N/A')} | "
                    f"Balance: {item.get('balance_qty', 'N/A')} | "
                    f"Purchased: {item.get('purchase_date', 'N/A')} | "
                    f"Created At: {item.get('created_at', 'N/A')} | "
                    f"Updated At: {item.get('updated_at', 'N/A')} | "
                    f"submitted_by: {item.get('submitted_by', 'N/A')}"
                    f"BarCode: {item.get('inventory_barcode', 'N/A')} | "
                )
                added_items_listbox.insert(tk.END, display_str)
        
        # Refresh form and generate new IDs
        update_main_inventory_list()
        refresh_form(scrollable_frame, header_labels)
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
        elif field in ['Purchase Date', 'Returned Date']:
            # Create a frame to hold the date entry and clear button
            date_frame = tk.Frame(scrollable_frame)
            date_frame.grid(row=row_num, column=col, sticky="ew", padx=1, pady=1)
            
            # Create DateEntry widget without setting a default date
            date_entry = DateEntry(
                date_frame,
                width=12,  # Slightly reduced to accommodate clear button
                background='darkblue',
                foreground='white',
                borderwidth=1,
                date_pattern='yyyy-mm-dd',
                font=('Helvetica', 9))
            date_entry.delete(0, 'end')  # Clear any default date
            date_entry.pack(side='left', fill=tk.X, expand=True)
            
            # Add clear button
            clear_btn = tk.Button(
                date_frame,
                text="✕",
                command=lambda e=date_entry: e.delete(0, 'end'),
                font=('Helvetica', 7),
                width=1,
                relief='flat',
            )
            clear_btn.pack(side='right', padx=(2,0))
            
            entries[var_name] = date_entry
        else:
            entries[var_name] = tk.Entry(
                scrollable_frame, 
                font=('Helvetica', 9), 
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=row_num, column=col, sticky='ew', padx=1, pady=1)
            
            # Pre-fill InventoryID and ProductID for new rows
            if field == 'InventoryID':
                entries[var_name].insert(0, generate_inventory_id())
                entries[var_name].config(state='readonly')
            elif field == 'ProductID':
                entries[var_name].insert(0, generate_product_id())
                entries[var_name].config(state='readonly')

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

def quit_application():
    """Confirm and quit the application"""
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

# Add this new function above the create_list_frames function:
def upload_inventory_with_message():
    """Upload inventory and show success message"""
    result = upload_inventory()
    if result:
        messagebox.showinfo("Success", "Inventory data uploaded successfully!")
    else:
        # The upload_inventory function already shows error messages
        pass

#  Adjust UI elements based on screen size
def configure_responsive_grid():
    """Adjust UI elements based on screen size"""
    clock_label.config(font=('Helvetica', 12, 'bold'))
    company_label.config(font=('Helvetica', 12))

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
    root.title("Tagglabs Inventory Management System")
    root.configure(bg='#f0f0f0')  # Light gray background
    
    # Use the imported maximize_window function
    maximize_window(root)
    
    return root

def open_reveal_window():
    """Open the Reveal QR & Barcode window"""
    RevealQrAndBarcodeWindow(root).open_reveal_qr_and_barcode_pop_up()

#  Create and configure the header frame with clock and company info
def create_header_frame(root):
    """Create and configure the header frame with clock and company info"""
    header_frame = tk.Frame(root, bg='#2c3e50', relief='raised', bd=2)
    header_frame.grid(row=0, column=0, sticky="nsew", padx=3, pady=1)
    
    # Configure grid for header frame
    header_frame.grid_columnconfigure(0, weight=1)
    header_frame.grid_rowconfigure(0, weight=1)
    header_frame.grid_rowconfigure(1, weight=1)
    
    # Row 1: Clock (top-center)
    global clock_label
    clock_label = tk.Label(header_frame, font=('Helvetica', 14, 'bold'), 
                          fg='white', bg='#2c3e50')
    clock_label.grid(row=0, column=0, sticky='n', pady=(8,0))
    
    # Row 2: Company info (bottom-right)
    company_info = """Tagglabs Experiential Pvt. Ltd.
        Sector 49, Gurugram, Haryana 122518
        251, Second Floor, Eros City Square Mall
        Eros City Square
        098214 43358"""
    
    global company_label
    company_label = tk.Label(header_frame,
                           text=company_info,
                           font=('Helvetica', 12),
                           justify='right',
                           anchor='ne',
                           fg='#ecf0f1', bg='#2c3e50')
    company_label.grid(row=1, column=0, sticky='ne', pady=(0,8), padx=12)
    
    return header_frame
    return header_frame

#  Create list frames with notebook tabs [Inventory List, New Entry, Search Results]
def create_list_frames(root):
    """Create list frames with notebook tabs"""
    # Calculate appropriate height to ensure all elements fit
    screen_height = root.winfo_screenheight()
    screen_width = root.winfo_screenwidth()
    
    # Reserve space for header (80px) and bottom buttons (120px)
    available_height = screen_height - 180
    list_frame_height = int(available_height * 0.8)
    listbox_height = max(8, list_frame_height // 35)  # Adjusted for larger fonts
    
    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, sticky="nsew", padx=3, pady=2)
    
    # Configure notebook style for modern tabs
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
    style.configure('TNotebook.Tab', 
                   padding=[20, 12], 
                   font=('Helvetica', 11, 'bold'),
                   background='#bdc3c7',
                   foreground='#2c3e50')
    style.map('TNotebook.Tab',
             background=[('selected', '#3498db'), ('active', '#5dade2')],
             foreground=[('selected', 'white'), ('active', 'white')])
    
    # Frame 1: Inventory List
    inventory_frame = tk.Frame(notebook, bg='white')
    notebook.add(inventory_frame, text="Inventory List")
    
    # Date range filter frame with modern styling
    date_filter_frame = tk.Frame(inventory_frame, bg='#ecf0f1', relief='raised', bd=1)
    date_filter_frame.pack(fill="x", pady=8, padx=8)
    
    global from_date_entry, to_date_entry
    
    # Left side controls
    left_frame = tk.Frame(date_filter_frame, bg='#ecf0f1')
    left_frame.pack(side="left", fill="x", expand=True, padx=12, pady=8)
    
    global from_date_entry, to_date_entry
    
    # Create standardized date range picker
    from_date_entry, to_date_entry = create_date_range_picker(left_frame, bg_color='#ecf0f1', start_column=0, row=0)
    
    # Modern styled buttons
    filter_btn = tk.Button(left_frame, text="Filter", command=filter_by_date_range,
                         font=('Helvetica', 12, 'bold'), height=1, width=12,
                         bg='#2c3e50', fg='white', relief='flat',
                         activebackground='#34495e', activeforeground='white')
    filter_btn.grid(row=0, column=4, padx=5)
    
    show_all_btn = tk.Button(left_frame, text="Show All", command=update_main_inventory_list,
                           font=('Helvetica', 12, 'bold'), height=1, width=12,
                           bg='#95a5a6', fg='white', relief='flat',
                           activebackground='#7f8c8d', activeforeground='white')
    show_all_btn.grid(row=0, column=5, padx=5)
    
    right_frame = tk.Frame(date_filter_frame, bg='#ecf0f1')
    right_frame.pack(side="right", fill="x", padx=12, pady=8)

    # Add Update button before Sync button
    update_btn = UpdatePopUpWindow.create_update_button(right_frame, root_window=root)
    update_btn.pack(side="right", padx=5)

    # Upload button with modern styling
    upload_btn = tk.Button(
        right_frame, 
        text="Upload", 
        command=lambda: upload_inventory_with_message(),
        font=('Helvetica', 12, 'bold'),
        height=1, width=12,
        bg='#34495e', fg='white', relief='flat',
        activebackground='#2c3e50', activeforeground='white'
    )
    upload_btn.pack(side="right", padx=5)

    # Sync button with modern styling
    sync_btn = tk.Button(
        right_frame, 
        text="Sync", 
        command=update_inventory_list,
        font=('Helvetica', 12, 'bold'),
        height=1, width=12,
        bg='#7f8c8d', fg='white', relief='flat',
        activebackground='#95a5a6', activeforeground='white'
    )
    sync_btn.pack(side="right", padx=5)

    # Add Update button
    UpdatePopUpWindow.create_update_button(inventory_frame, root_window=root)
    
    # Separator with modern styling
    separator = ttk.Separator(inventory_frame, orient='horizontal')
    separator.pack(fill="x", pady=8, padx=8)
        
    # Main List Container with modern styling
    list_container = tk.Frame(inventory_frame, bg='white', relief='sunken', bd=1)
    list_container.pack(fill="both", expand=True, padx=8, pady=(0,8))
    
    # Create horizontal scrollbar first (placed at bottom)
    h_scrollbar = tk.Scrollbar(
        list_container,
        orient="horizontal",
        command=lambda *args: inventory_listbox.xview(*args)
    )
    h_scrollbar.pack(side="bottom", fill="x")
    
    # Then create vertical scrollbar (right side)
    v_scrollbar = tk.Scrollbar(
        list_container,
        orient="vertical",
        command=lambda *args: inventory_listbox.yview(*args)
    )
    v_scrollbar.pack(side="right", fill="y")
    
    # Create the listbox with both scrollbars
    global inventory_listbox
    inventory_listbox = tk.Listbox(
        list_container,
        height=listbox_height,
        font=('Consolas', 12),
        activestyle='none',
        selectbackground='#3498db',
        selectforeground='white',
        bg='#ffffff',
        fg='#2c3e50',
        borderwidth=0,
        highlightthickness=0,
        xscrollcommand=h_scrollbar.set,
        yscrollcommand=v_scrollbar.set
    )
    inventory_listbox.pack(side="left", fill="both", expand=True)
    
    # Setup modern scrolling for inventory list
    setup_modern_scrolling(inventory_listbox)
    
    # Initialize the inventory list
    update_main_inventory_list()
    
    # Frame 2: New Entry
    create_new_entry_tab(notebook)
    
    # Frame 3: Search Results
    search_frame = tk.Frame(notebook, bg='white')
    notebook.add(search_frame, text="Search Results")

    # Search fields with modern styling
    search_fields_frame = tk.Frame(search_frame, bg='#ecf0f1', relief='raised', bd=1)
    search_fields_frame.pack(fill="x", pady=8, padx=8)
    
    for i in range(8):
        search_fields_frame.grid_columnconfigure(i, weight=1)

    global search_inventory_id_entry, search_project_id_entry, search_product_id_entry

    # Row 1: First three search fields
    tk.Label(search_fields_frame, text="Inventory ID:", font=('Helvetica', 12, 'bold'), 
            bg='#ecf0f1', fg='#2c3e50').grid(row=0, column=0, sticky='e', padx=5, pady=8)
    search_inventory_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 12), width=15,
                                       relief='flat', bd=5)
    search_inventory_id_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=8)

    tk.Label(search_fields_frame, text="Project ID:", font=('Helvetica', 12, 'bold'), 
            bg='#ecf0f1', fg='#2c3e50').grid(row=0, column=2, sticky='e', padx=5, pady=8)
    search_project_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 12), width=15,
                                     relief='flat', bd=5)
    search_project_id_entry.grid(row=0, column=3, sticky='ew', padx=5, pady=8)

    tk.Label(search_fields_frame, text="Product ID:", font=('Helvetica', 12, 'bold'), 
            bg='#ecf0f1', fg='#2c3e50').grid(row=0, column=4, sticky='e', padx=5, pady=8)
    search_product_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 12), width=15,
                                     relief='flat', bd=5)
    search_product_id_entry.grid(row=0, column=5, sticky='ew', padx=5, pady=8)

    # Search button with modern styling
    search_btn = tk.Button(search_fields_frame, text="Search", command=perform_search, 
                        font=('Helvetica', 12, 'bold'), height=1, width=12,
                        bg='#2c3e50', fg='white', relief='flat',
                        activebackground='#34495e', activeforeground='white')
    search_btn.grid(row=0, column=6, sticky='ew', padx=5, pady=8)

    # QR & Barcode button with modern styling
    reveal_btn = tk.Button(
        search_fields_frame,
        text="QR & Barcode", 
        font=('Helvetica', 12, 'bold'),
        width=15, height=1,
        bg='#95a5a6', fg='white', relief='flat',
        activebackground='#7f8c8d', activeforeground='white',
        command=open_reveal_window 
    )
    reveal_btn.grid(row=0, column=7, sticky='ew', padx=5, pady=8)
    # Make sure to adjust the column weights so the button stays on the right
    search_fields_frame.grid_columnconfigure(7, weight=1)

    # Separator line
    ttk.Separator(search_frame, orient='horizontal').pack(fill="x", pady=5)

    # Search Results list container
    search_list_container = tk.Frame(search_frame)
    search_list_container.pack(fill="both", expand=True)

    # Create horizontal scrollbar first (placed at bottom)
    h_scrollbar = tk.Scrollbar(
        search_list_container,
        orient="horizontal",
        command=lambda *args: search_results_listbox.xview(*args)
    )
    h_scrollbar.pack(side="bottom", fill="x")

    # Then create vertical scrollbar (right side)
    v_scrollbar = tk.Scrollbar(
        search_list_container,
        orient="vertical",
        command=lambda *args: search_results_listbox.yview(*args)
    )
    v_scrollbar.pack(side="right", fill="y")

    # Create the listbox with both scrollbars
    global search_results_listbox
    search_results_listbox = tk.Listbox(
        search_list_container,
        height=listbox_height,
        font=('Courier New', 11),
        activestyle='none',
        selectbackground='#4a6984',
        selectforeground='white',
        bg='white',
        fg='black',
        xscrollcommand=h_scrollbar.set,
        yscrollcommand=v_scrollbar.set
    )
    search_results_listbox.pack(side="left", fill="both", expand=True)
    
    # Setup modern scrolling for search results list
    setup_modern_scrolling(search_results_listbox)
    
    return notebook

def create_bottom_frames(root):
    """Create the bottom frames with modern styled action buttons"""
    bottom_frame = tk.Frame(root, bg='#34495e', relief='raised', bd=2)
    bottom_frame.grid(row=2, column=0, sticky='ew', padx=3, pady=3)
    bottom_frame.grid_columnconfigure(0, weight=1)
    
    button_container = tk.Frame(bottom_frame, bg='#34495e')
    button_container.pack(fill='x', padx=12, pady=8)
    
    left_buttons_frame = tk.Frame(button_container, bg='#34495e')
    left_buttons_frame.pack(side='left', fill='x', expand=True)
    
    buttons = [
        ("To Event", open_to_event, '#2c3e50'),
        ("From Event", open_from_event, '#34495e'),
        ("Assigned", open_assign_inventory, '#7f8c8d'),
        ("Damage/Waste", open_damage_inventory, '#95a5a6')
    ]
    
    for text, command, color in buttons:
        btn = tk.Button(
            left_buttons_frame,
            text=text,
            command=command,
            font=('Helvetica', 12, 'bold'),
            width=15,
            height=2,
            bg=color,
            fg='white',
            relief='flat',
            activebackground=color,
            activeforeground='white'
        )
        btn.pack(side='left', padx=3, fill='x', expand=True)
    
    quit_button = tk.Button(button_container, text="Quit", command=quit_application,
                          font=('Helvetica', 12, 'bold'), width=8, height=2,
                          bg='#95a5a6', fg='white', relief='flat',
                          activebackground='#7f8c8d', activeforeground='white')
    quit_button.pack(side='right', padx=5)

def configure_grid(root):
    """Configure the root grid layout"""
    root.grid_rowconfigure(0, weight=0)  # Header
    root.grid_rowconfigure(1, weight=1)  # List frames
    root.grid_rowconfigure(2, weight=0)  # Bottom buttons
    root.grid_columnconfigure(0, weight=1)  # Single column for full width

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

    # Setup clock update using the imported function
    setup_clock_update(root, clock_label)
    
    # Setup window closing handler using the imported function
    setup_window_closing(root)

    root.mainloop()

if __name__ == "__main__":
    main()