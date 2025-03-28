import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import platform
import logging

from backend.app.routers.inventory import fetch_inventory, add_inventory, search_inventory, get_inventory_by_date_range
from .to_event import ToEventWindow
from .from_event import FromEventWindow
from .assign_inventory import AssignInventoryWindow
from .damage_inventory import DamageWindow

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('inventory_system.log')
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

def update_main_inventory_list():
    """Update only the main inventory listbox with all items"""
    if inventory_listbox:
        inventory_listbox.delete(0, tk.END)
        try:
            inventory = fetch_inventory()
            display_inventory_items(inventory)
        except Exception as e:
            logger.error(f"Failed to fetch inventory: {e}")
            messagebox.showerror("Error", "Could not fetch inventory data")

def display_inventory_items(items):
    """Display inventory items in the listbox"""
    if inventory_listbox:
        inventory_listbox.delete(0, tk.END)
        for item in items:
            inventory_listbox.insert(tk.END, 
                f"{item['S No']} | {item['InventoryID']} | {item['Product ID']} | {item['Name']} | "
                f"{item['Qty']} | {'Yes' if item['Purchase'] else 'No'} | "
                f"{item['Purchase Date']} | {item['Purchase Amount']}")

def filter_by_date_range():
    """Filter inventory items by date range"""
    from_date = from_date_entry.get()
    to_date = to_date_entry.get()
    
    if not from_date or not to_date:
        messagebox.showwarning("Warning", "Please select both From and To dates")
        return
    
    try:
        # Convert dates to proper format if needed
        from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
        
        if from_date_obj > to_date_obj:
            messagebox.showwarning("Warning", "From date cannot be after To date")
            return
            
        items = get_inventory_by_date_range(from_date, to_date)
        display_inventory_items(items)
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Failed to filter by date range: {e}")
        messagebox.showerror("Error", "Could not filter inventory by date range")

def perform_search():
    """Perform inventory search based on search criteria"""
    inventory_id = search_inventory_id_entry.get().strip()
    project_id = search_project_id_entry.get().strip()
    product_id = search_product_id_entry.get().strip()
    
    if search_results_listbox:
        search_results_listbox.delete(0, tk.END)
    
    try:
        results = search_inventory(
            inventory_id=inventory_id if inventory_id else None,
            project_id=project_id if project_id else None,
            product_id=product_id if product_id else None
        )
        
        if not results:
            messagebox.showinfo("Search Results", "No matching items found")
            return
            
        for item in results:
            if search_results_listbox:
                search_results_listbox.insert(tk.END, 
                    f"{item['S No']} | {item['InventoryID']} | {item['Product ID']} | {item['Name']} | "
                    f"{item['Qty']} | {'Yes' if item['Purchase'] else 'No'} | "
                    f"{item['Purchase Date']} | {item['Purchase Amount']}")
                
    except Exception as e:
        logger.error(f"Search failed: {e}")
        messagebox.showerror("Search Error", "Failed to perform search")

def add_inventory_item():
    """Add a new inventory item based on form data"""
    item = {}
    required_fields = ['SNo', 'InventoryID', 'ProductID', 'Name', 'TotalQuantity', 
                      'PurchaseDate', 'PurchaseAmount', 'VendorName', 'TotalRent']
    
    # Validate required fields
    for key in required_fields:
        if key in entries and isinstance(entries[key], tk.Entry):
            value = entries[key].get().strip()
            if not value:
                messagebox.showerror("Error", f"{key} field is required")
                return
            if key in ['TotalQuantity', 'PurchaseAmount', 'TotalRent']:
                try:
                    item[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    messagebox.showerror("Error", f"{key} must be a number")
                    return
            else:
                item[key] = value
    
    # Get checkbox values
    for key, var in checkbox_vars.items():
        item[key] = var.get()

    # Get other fields
    optional_fields = ['ReturnedDate']
    for field in optional_fields:
        if field in entries and isinstance(entries[field], tk.Entry):
            item[field] = entries[field].get().strip()

    try:
        added_item = add_inventory(item)
        if added_items_listbox:
            added_items_listbox.insert(tk.END, 
                f"{added_item['S No']} | {added_item['InventoryID']} | {added_item['Product ID']} | {added_item['Name']} | "
                f"{added_item['Qty']} | {'Yes' if added_item['Purchase'] else 'No'} | "
                f"{added_item['Purchase Date']} | {added_item['Purchase Amount']}")
        clear_fields()
        update_main_inventory_list()
    except Exception as e:
        logger.error(f"Failed to add inventory item: {e}")
        messagebox.showerror("Error", "Could not add inventory item")

def update_clock():
    """Update the clock label with current time"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clock_label.config(text=now)
    root.after(1000, update_clock)

def quit_application():
    """Confirm and quit the application"""
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def configure_responsive_grid():
    """Adjust UI elements based on screen size"""
    screen_width = root.winfo_screenwidth()
    font_size = max(6, screen_width // 100)

    clock_label.config(font=('Helvetica', 8))
    company_label.config(font=('Helvetica', 7))

# Child window functions
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
    
    # Date range filter frame
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
    
    # Sync button
    sync_btn = tk.Button(right_frame, text="Sync", command=update_inventory_list,
                       font=('Helvetica', 9, 'bold'))
    sync_btn.pack(side="right", padx=5)
    
    # Separator
    ttk.Separator(inventory_frame, orient='horizontal').pack(fill="x", pady=5)
    
    # Main List Container
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
    
    # Frame 2: New Entry
    new_entry_frame = tk.Frame(notebook)
    notebook.add(new_entry_frame, text="New Entry")

    # Create main container with vertical scroll
    entry_container = tk.Frame(new_entry_frame)
    entry_container.pack(fill='both', expand=True)

    # Create canvas and scrollbar
    entry_canvas = tk.Canvas(entry_container)
    entry_scrollbar = tk.Scrollbar(entry_container, orient='vertical', command=entry_canvas.yview)
    entry_scrollable_frame = tk.Frame(entry_canvas)

    entry_scrollable_frame.bind(
        "<Configure>",
        lambda e: entry_canvas.configure(
            scrollregion=entry_canvas.bbox("all")
        )
    )

    entry_canvas.create_window((0, 0), window=entry_scrollable_frame, anchor='nw')
    entry_canvas.configure(yscrollcommand=entry_scrollbar.set)

    entry_canvas.pack(side='left', fill='both', expand=True)
    entry_scrollbar.pack(side='right', fill='y')

    # Create the entry form inside the scrollable frame
    global entries, checkbox_vars
    entries = {}
    checkbox_vars = {}

    # Header row with field names
    header_labels = [
        'Sno.', "InventoryID", "ProductID", 'Name', 'Material', 'Total Quantity', 
        'Manufacturer', 'Purchase Dealer', 'Purchase Date', 'Purchase Amount', 
        'Repair Quantity', 'Repair Cost', 'On Rent', 'Vendor Name', 'Total Rent', 
        'Rented Inventory Returned', 'Returned Date', 'On Event', 'In Office', 
        'In Warehouse', 'Issued Qty', 'Balance Qty'
    ]

    # Create header row
    for col, label in enumerate(header_labels):
        header = tk.Label(entry_scrollable_frame, text=label, 
                         font=('Helvetica', 9, 'bold'), borderwidth=1, relief='solid')
        header.grid(row=0, column=col, sticky='ew', padx=1, pady=1)

    # Input fields row
    for col, field in enumerate(header_labels):
        var_name = field.replace(' ', '')
        if field in ['On Rent', 'Rented Inventory Returned', 'On Event', 'In Office', 'In Warehouse']:
            checkbox_vars[var_name] = tk.BooleanVar()
            entries[var_name] = tk.Checkbutton(
                entry_scrollable_frame, 
                variable=checkbox_vars[var_name],
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=1, column=col, sticky='ew', padx=1, pady=1)
        else:
            entries[var_name] = tk.Entry(
                entry_scrollable_frame, 
                font=('Helvetica', 9), 
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=1, column=col, sticky='ew', padx=1, pady=1)

    # Configure column weights to make them expandable
    for col in range(len(header_labels)):
        entry_scrollable_frame.grid_columnconfigure(col, weight=1)

    # Add Item button
    add_button = tk.Button(
        entry_scrollable_frame, 
        text="Add Item", 
        command=add_inventory_item,
        font=('Helvetica', 10, 'bold')
    )
    add_button.grid(row=2, column=0, columnspan=len(header_labels), pady=10, sticky='ew')

    # Added Items List display
    list_label = tk.Label(
        entry_scrollable_frame, 
        text="Added Items List", 
        font=('Helvetica', 10, 'bold')
    )
    list_label.grid(row=3, column=0, columnspan=len(header_labels), pady=5, sticky='ew')

    # Create container frame for the listbox
    list_container = tk.Frame(entry_scrollable_frame)
    list_container.grid(row=4, column=0, columnspan=len(header_labels), sticky='nsew', padx=5, pady=5)
    
    # Configure container grid
    list_container.grid_rowconfigure(0, weight=1)
    list_container.grid_columnconfigure(0, weight=1)

    # Create the listbox
    global added_items_listbox
    added_items_listbox = tk.Listbox(
        list_container,
        height=15,
        font=('Helvetica', 9),
        selectbackground='#4a6984',
        selectforeground='white',
        borderwidth=1,
        relief='solid'
    )
    added_items_listbox.grid(row=0, column=0, sticky='nsew')

    # Add scrollbar
    list_scrollbar = tk.Scrollbar(
        list_container,
        orient='vertical',
        command=added_items_listbox.yview
    )
    list_scrollbar.grid(row=0, column=1, sticky='ns')
    added_items_listbox.config(yscrollcommand=list_scrollbar.set)

    # Configure row weights for the scrollable frame
    entry_scrollable_frame.grid_rowconfigure(4, weight=1)  # Make the list row expandable
    
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