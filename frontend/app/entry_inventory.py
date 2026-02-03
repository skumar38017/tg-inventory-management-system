#  frontend/app/entry_inventory.py
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
from damage_inventory import DamageWindow
from homePage.entry_update_pop_window import *
from homePage.reveal_qr_barcode_window import *
from homePage.new_entry import create_new_entry_tab
from homePage.entry_update_pop_window import UpdatePopUpWindow
from homePage.search_results import SearchResults
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

# Global pagination instance
paginator = Pagination()

# Global variables for pagination UI
page_info_label = None
page_entry = None

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
        
# Update main inventory listbox with all items by clicking sync button
def update_main_inventory_list():
    """Update only the main inventory listbox with paginated items"""
    if inventory_listbox:
        # Clear existing items from treeview
        for item in inventory_listbox.get_children():
            inventory_listbox.delete(item)
        try:
            inventory = show_all_inventory()  # Returns 20 items for current page
            display_inventory_items(inventory)
            update_pagination_info()
        except Exception as e:
            logger.error(f"Failed to Sync inventory: {e}")
            custom_messagebox("error", "Error", "Could not Sync inventory data")

def update_pagination_info():
    """Update pagination display info"""
    current_page = get_current_page()
    # You can add pagination info display here if needed
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
        page_num = int(page_entry.get())
        if page_num >= 0:
            paginator.go_to_page(page_num)
            update_main_inventory_list()
    except ValueError:
        custom_messagebox("warning", "Invalid Page", "Please enter a valid page number")

def update_pagination_ui():
    """Update pagination UI elements"""
    global paginator
    if page_info_label:
        current_page = paginator.current_page
        page_info_label.config(text=f"Page {current_page} | 20 items per page")
    
    if page_entry:
        page_entry.delete(0, tk.END)
        page_entry.insert(0, str(paginator.current_page))

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
            
#  Filter inventory by date range by `filter` button
def filter_by_date_range():
    """Filter inventory items by date range"""
    from_date_str = from_date_entry.get()
    to_date_str = to_date_entry.get()
    
    if not from_date_str or not to_date_str:
          custom_messagebox("warning", "Warning", "Please select both From and To dates")
          return
    try:
        # Convert dates to proper format if needed
        from_date_obj = datetime.strptime(from_date_str, "%Y-%m-%d")
        to_date_obj = datetime.strptime(to_date_str, "%Y-%m-%d")
        
        if from_date_obj > to_date_obj:
            custom_messagebox("warning", "Warning", "From date cannot be after To date")
            return
            
        # Pass the date strings directly
        items = filter_inventory_by_date_range(from_date_str, to_date_str)
        display_inventory_items(items)
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        custom_messagebox("error", "Error", "Invalid date format. Please use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Failed to filter by date range: {e}")
        custom_messagebox("error", "Error", "Could not filter inventory by date range")

# Perform inventory search based on search criteria [InventoryID, 'ProjectID', ProductID]
# Moved to homePage/search_results.py

# Add new inventory items from all rows

def quit_application():
    """Confirm and quit the application"""
    if custom_confirmation("Quit", "Do you really want to quit?"):
        root.destroy()

# Add this new function above the create_list_frames function:
def upload_inventory_with_message():
    """Upload inventory and show success message"""
    result = upload_inventory()
    if result:
        custom_messagebox("info", "Success", "Inventory data uploaded successfully!")
    else:
        # The upload_inventory function already shows error messages
        pass

#  Adjust UI elements based on screen size
def configure_responsive_grid():
    """Adjust UI elements based on screen size"""
    clock_label.config(font=(universal_font_box_size.qr_barcode_header_font_family, 12, 'bold'))
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
    clock_label = tk.Label(header_frame, font=(universal_font_box_size.qr_barcode_header_font_family, 14, 'bold'), 
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
                           font=(universal_font_box_size.qr_barcode_header_font_family, 12),
                           justify='right',
                           anchor='ne',
                           fg='#ecf0f1', bg='#2c3e50')
    company_label.grid(row=1, column=0, sticky='ne', pady=(0,8), padx=12)
    
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
    listbox_height = universal_font_box_size.button_width_medium # Increased row height
    
    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, sticky="nsew", padx=3, pady=2)
    
    # Configure notebook style for modern tabs
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
                         font=(universal_font_box_size.qr_barcode_header_font_family, 12, 'bold'), height=1, width=12,
                         bg='#2c3e50', fg='white', relief='flat',
                         activebackground='#34495e', activeforeground='white')
    filter_btn.grid(row=0, column=4, padx=5)
    
    show_all_btn = tk.Button(left_frame, text="Show All", command=update_main_inventory_list,
                           font=(universal_font_box_size.qr_barcode_header_font_family, 12, 'bold'), height=1, width=12,
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
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_large, 'bold'),
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
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_large, 'bold'),
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
    
    # Create the inventory table with Treeview
    global inventory_listbox
    
    # Smart column definition - just names, loop handles the rest
    columns = ['ID','Serial No.', 'InventoryID', 'ProductID', 'Name', 'Material', 'Total Quantity', 
               'Manufacturer', 'Purchase Dealer', 'Purchase Date', 'Purchase Amount', 
               'Repair Quantity', 'Repair Cost', 'On Rent', 'Vendor Name', 'Total Rent', 
               'Rented Returned', 'Returned Date', 'On Event', 'In Office', 
               'In Warehouse', 'Issued Qty', 'Balance Qty', 'Bar Code', 'Barcode URL', 
               'QrCodeUrl', 'Created At', 'Updated At', 'Submitted by'
            ]
    
    inventory_listbox = ttk.Treeview(list_container, columns=columns, show='headings', height=listbox_height)
    
    # Configure uniform column widths for equal rectangular cells  
    uniform_width = 500  # Fixed width for all columns to create equal rectangles
    for col in columns:
        inventory_listbox.heading(col, text=col, anchor="center")
        inventory_listbox.column(col, width=uniform_width, minwidth=uniform_width, anchor='center', stretch=False)
    
    # Ensure headers scroll with data by binding xview events
    def sync_header_scroll(*args):
        """Synchronize header scrolling with data"""
        inventory_listbox.xview(*args)
    
    # Override the horizontal scrollbar command to ensure header sync
    h_scrollbar.config(command=sync_header_scroll)
    
    # Ensure headers stay synchronized with data during horizontal scrolling
    inventory_listbox.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
    v_scrollbar.config(command=inventory_listbox.yview)
    
    inventory_listbox.pack(side="left", fill="both", expand=True)
    
    # Bind arrow key scrolling with header sync
    def scroll_left(event):
        """Scroll table left with arrow key"""
        sync_header_scroll("scroll", -1, "units")
        return "break"
    
    def scroll_right(event):
        """Scroll table right with arrow key"""
        sync_header_scroll("scroll", 1, "units")
        return "break"
    
    def scroll_up(event):
        """Scroll table up with arrow key"""
        inventory_listbox.yview_scroll(-50, "units")
        return "break"
    
    def scroll_down(event):
        """Scroll table down with arrow key"""
        inventory_listbox.yview_scroll(50, "units")
        return "break"
    
    # Bind keys to inventory listbox
    inventory_listbox.bind('<Left>', scroll_left)
    inventory_listbox.bind('<Right>', scroll_right)
    inventory_listbox.bind('<Up>', scroll_up)
    inventory_listbox.bind('<Down>', scroll_down)
    inventory_listbox.focus_set()  # Allow keyboard focus
    
    # Styling
    style = ttk.Style()
    style.configure('Treeview', font=(universal_font_box_size.qr_barcode_title_font_family))
    style.configure("Treeview", rowheight=universal_font_box_size.input_height)  # Increase row height to 40 pixels
    style.configure('Treeview.Heading', font=(universal_font_box_size.qr_barcode_title_font_family))
    style.configure('Treeview.Heading', rowheight=universal_font_box_size.input_height)
    
    # Excel-like grid appearance with uniform rectangular cells
    style.configure("Treeview", 
                   relief="solid", 
                   borderwidth=1,
                   fieldbackground="white",
                   rowheight=35)  # Fixed row height for uniform rectangles
    style.configure("Treeview.Heading", 
                   relief="solid", 
                   borderwidth=1,
                   background="#d4e6f1",
                   foreground="black",
                   anchor="center")  # Center align headers

    inventory_listbox.tag_configure('evenrow', background='#f5f5f5')  # Official gray
    inventory_listbox.tag_configure('oddrow', background='#ffffff')   # Pure white
    
    setup_modern_scrolling(inventory_listbox)
    
    # Initialize the inventory list
    update_main_inventory_list()
    
    # Frame 2: New Entry
    create_new_entry_tab(notebook)
    
    # Frame 3: Search Results - using SearchResults class
    search_results = SearchResults(root)
    search_results.create_search_results_tab(notebook)
    
    return notebook

def create_pagination_frame(root):
    """Create pagination controls between display list and bottom buttons"""
    global page_info_label, page_entry
    
    # Pagination frame
    pagination_frame = tk.Frame(root, bg='#ecf0f1', height=60, relief='raised', bd=1)
    pagination_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=5)
    pagination_frame.grid_propagate(False)
    
    # Left side - Page info
    page_info_label = tk.Label(
        pagination_frame,
        text="Page 0 | 20 items per page",
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_small),
        bg='#ecf0f1', fg='#2c3e50'
    )
    page_info_label.pack(side="left", padx=20, pady=15)
    
    # Right side - Navigation buttons
    nav_frame = tk.Frame(pagination_frame, bg='#ecf0f1')
    nav_frame.pack(side="right", padx=20, pady=10)
    
    # First page button
    first_btn = tk.Button(
        nav_frame,
        text="<<",
        command=go_to_first_page,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_medium, 'bold'),
        width=4, height=1,
        bg='#95a5a6', fg='white', relief='flat', bd=1,
        activebackground='#7f8c8d', activeforeground='white'
    )
    first_btn.pack(side="left", padx=3)
    
    # Previous button
    prev_btn = tk.Button(
        nav_frame,
        text="<",
        command=go_prev_page,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_medium, 'bold'),
        width=4, height=1,
        bg='#3498db', fg='white', relief='flat', bd=1,
        activebackground='#2980b9', activeforeground='white'
    )
    prev_btn.pack(side="left", padx=3)
    
    # Page number entry
    page_entry = tk.Entry(
        nav_frame,
        width=6,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_medium),
        justify='center', relief='solid', bd=1
    )
    page_entry.pack(side="left", padx=5)
    page_entry.insert(0, "0")
    page_entry.bind('<Return>', lambda e: go_to_page_from_entry())
    
    # Next button
    next_btn = tk.Button(
        nav_frame,
        text=">",
        command=go_next_page,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_medium, 'bold'),
        width=4, height=1,
        bg='#3498db', fg='white', relief='flat', bd=1,
        activebackground='#2980b9', activeforeground='white'
    )
    next_btn.pack(side="left", padx=3)

def create_bottom_frames(root):
    """Create the bottom frames with modern styled action buttons"""
    bottom_frame = tk.Frame(root, bg='#34495e', relief='raised', bd=2)
    bottom_frame.grid(row=3, column=0, sticky='ew', padx=3, pady=3)
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
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_large, 'bold'),
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
                          font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_large, 'bold'), width=8, height=2,
                          bg='#95a5a6', fg='white', relief='flat',
                          activebackground='#7f8c8d', activeforeground='white')
    quit_button.pack(side='right', padx=5)

def configure_grid(root):
    """Configure the root grid layout"""
    root.grid_rowconfigure(0, weight=0)  # Header
    root.grid_rowconfigure(1, weight=1)  # List frames
    root.grid_rowconfigure(2, weight=0)  # Pagination
    root.grid_rowconfigure(3, weight=0)  # Bottom buttons
    root.grid_columnconfigure(0, weight=1)  # Single column for full width

def main():
    """Main application entry point"""
    global root
    root = setup_main_window()
    
    # Create frames in order
    header_frame = create_header_frame(root)  # Row 0: Clock and company info
    notebook = create_list_frames(root)      # Row 1: Display lists (includes initial update)
    create_pagination_frame(root)            # Row 1.5: Pagination controls
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