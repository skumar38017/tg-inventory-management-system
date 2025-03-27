# frontend/app/entry_inventory.py

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import platform
import logging

from backend.app.routers.inventory import fetch_inventory, add_inventory
from .to_event import ToEventWindow
from .from_event import FromEventWindow
from .assign_inventory import AssignInventoryWindow
from .damage_inventory import DamageWindow  # Fixed typo in filename (inventoty -> inventory)

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

def clear_fields():
    """Clear all input fields and reset checkboxes"""
    for entry in entries.values():
        if isinstance(entry, tk.Entry):
            entry.delete(0, tk.END)
    for var in checkbox_vars.values():
        var.set(False)

def update_inventory_list():
    """Update the inventory listbox with current inventory data"""
    inventory_listbox.delete(0, tk.END)
    try:
        inventory = fetch_inventory()
        for item in inventory:
            inventory_listbox.insert(tk.END, 
                f"{item['S No']} | {item['InventoryID']} | {item['Product ID']} | {item['Name']} | "
                f"{item['Qty']} | {'Yes' if item['Purchase'] else 'No'} | "
                f"{item['Purchase Date']} | {item['Purchase Amount']} | {'Yes' if item['On Rent'] else 'No'} | "
                f"{item['Vendor Name']} | {item['Total Rent']} | "
                f"{'Yes' if item['Rented Inventory Returned'] else 'No'} | {item['Returned Date']} | "
                f"{'Yes' if item['On Event'] else 'No'} | {'Yes' if item['In Office'] else 'No'} | "
                f"{'Yes' if item['In Warehouse'] else 'No'} | {item['Inventory Barcode']}")
    except Exception as e:
        logger.error(f"Failed to fetch inventory: {e}")
        messagebox.showerror("Error", "Could not fetch inventory data")

def add_inventory_item():
    """Add a new inventory item based on form data"""
    item = {}
    required_fields = ['S No', 'InventoryID', 'Product ID', 'Name', 'Qty', 
                      'Purchase Date', 'Purchase Amount', 'Vendor Name', 'Total Rent']
    
    # Validate required fields
    for key in required_fields:
        if key in entries and isinstance(entries[key], tk.Entry):
            value = entries[key].get().strip()
            if not value:
                messagebox.showerror("Error", f"{key} field is required")
                return
            if key in ['Qty', 'Purchase Amount', 'Total Rent']:
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
    optional_fields = ['Returned Date', 'Inventory Barcode']
    for field in optional_fields:
        if field in entries and isinstance(entries[field], tk.Entry):
            item[field] = entries[field].get().strip()

    try:
        add_inventory(item)
        clear_fields()
        update_inventory_list()
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

    for label in labels.values():
        label.config(font=('Helvetica', font_size), anchor='w')
    for entry in entries.values():
        if isinstance(entry, tk.Entry):
            entry.config(font=('Helvetica', font_size), width=12)

    clock_label.config(font=('Helvetica', 8))
    company_label.config(font=('Helvetica', 7))
#  --------------------------------------------------------------------------------------------------
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
    global root  # Add this line to modify the module-level variable
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
    """Create and configure the header frame"""
    header_frame = tk.Frame(root)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=0)
    
    # Configure grid for header frame
    header_frame.grid_columnconfigure(0, weight=1)  # Center column expands
    header_frame.grid_rowconfigure(0, weight=1)     # Row 0 for clock
    header_frame.grid_rowconfigure(1, weight=1)     # Row 1 for company info
    
    # Clock label - centered at top (row 0)
    global clock_label
    clock_label = tk.Label(header_frame, font=('Helvetica', 8))
    clock_label.grid(row=0, column=0, sticky='n', pady=(0,0))
    
    # Company info - top-right corner (row 1)
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

def create_form_frame(root):
    """Create the form frame with horizontal scrolling"""
    form_container = tk.Frame(root)
    form_container.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
    form_container.grid_columnconfigure(0, weight=1)
    
    canvas = tk.Canvas(form_container)
    scrollbar = tk.Scrollbar(form_container, orient="horizontal", command=canvas.xview)
    scrollbar.pack(side="bottom", fill="x")
    canvas.pack(side="top", fill="both", expand=True)
    canvas.configure(xscrollcommand=scrollbar.set)
    
    form_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=form_frame, anchor="nw")
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.xview_moveto(0)
    
    form_frame.bind("<Configure>", on_frame_configure)
    
    return form_container, form_frame

def create_input_fields(form_frame):
    """Create input fields and labels"""
    global labels, entries, checkbox_vars
    labels = {}
    entries = {}
    checkbox_vars = {}
    
    fields = [
        'Sno.', "InventoryID", "ProductID", 'Name', 'Qty', 'Purchase',
        'Purchase Date', 'Purchase Amount', 'On Rent',
        'Vendor Name', 'Total Rent', 'Rented Inventory Returned', 
        'Returned Date', 'On Event', 'In Office', 'In Warehouse', 
        'Inventory Barcode'
    ]
    
    for col, field in enumerate(fields):
        label_text = field.replace('_', ' ').title()
        labels[field] = tk.Label(form_frame, text=label_text, 
                                font=('Helvetica', 10), anchor='w')
        
        if field in ['Purchase', 'On Rent', 'Rented Inventory Returned', 
                    'On Event', 'In Office', 'In Warehouse']:
            checkbox_vars[field] = tk.BooleanVar()
            entries[field] = tk.Checkbutton(form_frame, variable=checkbox_vars[field])
        else:
            entries[field] = tk.Entry(form_frame, width=12)
        
        labels[field].grid(row=0, column=col, padx=5, pady=2, sticky='w')
        
        if field in ['On Rent', 'On Event', 'In Office', 'In Warehouse']:
            entries[field].grid(row=1, column=col, padx=5, pady=2)
        else:
            entries[field].grid(row=1, column=col, padx=5, pady=2, sticky='ew')

def create_button_frame(root):
    """Create the button frame with action buttons"""
    button_frame = tk.Frame(root)
    button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
    button_frame.grid_columnconfigure(0, weight=1)
    
    add_button = tk.Button(button_frame, text="Add Item", command=add_inventory_item,
                          font=('Helvetica', 10, 'bold'))
    add_button.pack(expand=True, pady=5)
    
    return button_frame

def create_list_frame(root):
    """Create the inventory list display"""
    list_frame = tk.Frame(root)
    list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)
    
    global inventory_listbox
    inventory_listbox = tk.Listbox(
        list_frame,
        height=15,
        font=('Helvetica', 9),
        activestyle='none',
        selectbackground='#4a6984',
        selectforeground='white'
    )
    inventory_listbox.grid(row=0, column=0, sticky="nsew")
    
    list_scrollbar = tk.Scrollbar(
        list_frame,
        orient="vertical",
        command=inventory_listbox.yview
    )
    list_scrollbar.grid(row=0, column=1, sticky="ns")
    inventory_listbox.config(yscrollcommand=list_scrollbar.set)
    
    return list_frame

def create_bottom_frames(root):
    """Create the bottom frames with action buttons"""
    # Bottom-left buttons
    bottom_left_frame = tk.Frame(root)
    bottom_left_frame.grid(row=4, column=0, sticky='sw', padx=10, pady=10)
    
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
    quit_frame.grid(row=4, column=1, sticky='se', padx=10, pady=10)
    
    quit_button = tk.Button(quit_frame, text="Quit", command=quit_application,
                          font=('Helvetica', 10, 'bold'), width=10)
    quit_button.pack()

def configure_grid(root):
    """Configure the root grid layout"""
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=0)
    root.grid_rowconfigure(2, weight=0)
    root.grid_rowconfigure(3, weight=1)  # Most weight to list frame
    root.grid_rowconfigure(4, weight=0)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

def main():
    """Main application entry point"""
    global root
    root = setup_main_window()
    
    header_frame = create_header_frame(root)
    form_container, form_frame = create_form_frame(root)
    create_input_fields(form_frame)
    button_frame = create_button_frame(root)
    list_frame = create_list_frame(root)
    create_bottom_frames(root)
    configure_grid(root)
    
    # Initialize
    update_inventory_list()
    configure_responsive_grid()
    root.bind('<Configure>', lambda e: configure_responsive_grid())
    update_clock()
    root.protocol("WM_DELETE_WINDOW", quit_application)
    
    root.mainloop()