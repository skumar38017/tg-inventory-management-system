import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import time
import platform

from .inventory import fetch_inventory, add_inventory

def clear_fields():
    name_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)
    purchased_entry.delete(0, tk.END)
    on_event_var.set(False)
    in_office_var.set(False)
    warehouse_var.set(False)
    on_rent_var.set(False)
    vendor_name_entry.delete(0, tk.END)

def update_inventory_list():
    inventory_listbox.delete(0, tk.END)
    inventory = fetch_inventory()
    for item in inventory:
        inventory_listbox.insert(tk.END, f"{item['name']} - {item['qty']} - {item['vendor_name']}")

def add_inventory_item():
    name = name_entry.get()
    description = description_entry.get()
    qty = qty_entry.get()
    purchased = purchased_entry.get()
    on_event = on_event_var.get()
    in_office = in_office_var.get()
    warehouse = warehouse_var.get()
    on_rent = on_rent_var.get()
    vendor_name = vendor_name_entry.get()

    if not all([name, description, qty, purchased, vendor_name]):
        messagebox.showerror("Error", "All fields are required")
        return

    item = {
        "name": name,
        "description": description,
        "qty": int(qty),
        "purchased": purchased,
        "on_event": on_event,
        "in_office": in_office,
        "warehouse": warehouse,
        "on_rent": on_rent,
        "vendor_name": vendor_name
    }

    add_inventory(item)
    clear_fields()
    update_inventory_list()

def update_clock():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clock_label.config(text=now)
    root.after(1000, update_clock)

def quit_application():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def configure_responsive_grid():
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    min_col_width = max(100, screen_width // 20)
    entry_width = max(20, screen_width // 80)
    font_size = max(8, screen_height // 60)
    
    root.grid_columnconfigure(0, weight=1, minsize=min_col_width)
    root.grid_columnconfigure(1, weight=1, minsize=min_col_width*2)
    
    font_style = ('Helvetica', font_size)
    bold_font = ('Helvetica', font_size, 'bold')
    
    for widget in root.winfo_children():
        if isinstance(widget, (tk.Label, tk.Button)):
            widget.config(font=font_style)
    
    clock_label.config(font=('Helvetica', 8))  # Tiny font for clock
    company_label.config(font=('Helvetica', 7))
    
    name_entry.config(width=entry_width)
    description_entry.config(width=entry_width)
    qty_entry.config(width=entry_width)
    purchased_entry.config(width=entry_width)
    vendor_name_entry.config(width=entry_width)
    inventory_listbox.config(width=entry_width*2, height=screen_height//50)

# Create the main window
root = tk.Tk()
root.title("Tagglabs's Inventory")

# Cross-platform window maximization
try:
    root.state('zoomed')  # Windows
except tk.TclError:
    try:
        if platform.system() == 'Linux':
            root.attributes('-zoomed', True)  # Some Linux systems
        else:
            root.attributes('-fullscreen', True)  # macOS and others
    except:
        # Fallback to setting window size manually
        root.geometry("{0}x{1}+0+0".format(
            root.winfo_screenwidth(), 
            root.winfo_screenheight()
        ))

# Top frame for clock and company info
top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

# Clock label - centered at top
clock_label = tk.Label(top_frame, font=('Helvetica', 8))
clock_label.pack(pady=(0, 5))  # Small padding below clock

# Company info frame - aligned to right
company_frame = tk.Frame(top_frame)
company_frame.pack(anchor='e')

company_info = """Tagglabs Experiential Pvt. Ltd.
Sector 49, Gurugram, Haryana 122018
201, Second Floor, Eros City Square Mall
Eros City Square
098214 43358"""

company_label = tk.Label(company_frame, 
                        text=company_info,
                        font=('Helvetica', 7),
                        justify=tk.RIGHT)
company_label.pack()

# Form frame
form_frame = tk.Frame(root)
form_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

for i in range(10):
    form_frame.grid_rowconfigure(i, weight=1)
form_frame.grid_columnconfigure(0, weight=1)
form_frame.grid_columnconfigure(1, weight=2)

# Form widgets
tk.Label(form_frame, text="Name:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky='e', padx=5, pady=2)
name_entry = tk.Entry(form_frame)
name_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

tk.Label(form_frame, text="Description:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=5, pady=2)
description_entry = tk.Entry(form_frame)
description_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

tk.Label(form_frame, text="Quantity:", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky='e', padx=5, pady=2)
qty_entry = tk.Entry(form_frame)
qty_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

tk.Label(form_frame, text="Purchased:", font=('Helvetica', 10, 'bold')).grid(row=3, column=0, sticky='e', padx=5, pady=2)
purchased_entry = tk.Entry(form_frame)
purchased_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

# Checkboxes
on_event_var = tk.BooleanVar()
tk.Checkbutton(form_frame, text="On Event", variable=on_event_var, font=('Helvetica', 10)).grid(row=4, column=1, sticky='w', padx=5, pady=2)

in_office_var = tk.BooleanVar()
tk.Checkbutton(form_frame, text="In Office", variable=in_office_var, font=('Helvetica', 10)).grid(row=5, column=1, sticky='w', padx=5, pady=2)

warehouse_var = tk.BooleanVar()
tk.Checkbutton(form_frame, text="Warehouse", variable=warehouse_var, font=('Helvetica', 10)).grid(row=6, column=1, sticky='w', padx=5, pady=2)

on_rent_var = tk.BooleanVar()
tk.Checkbutton(form_frame, text="On Rent", variable=on_rent_var, font=('Helvetica', 10)).grid(row=7, column=1, sticky='w', padx=5, pady=2)

tk.Label(form_frame, text="Vendor Name:", font=('Helvetica', 10, 'bold')).grid(row=8, column=0, sticky='e', padx=5, pady=2)
vendor_name_entry = tk.Entry(form_frame)
vendor_name_entry.grid(row=8, column=1, sticky='ew', padx=5, pady=2)

# Add button only in form frame
add_button = tk.Button(form_frame, text="Add Item", command=add_inventory_item, font=('Helvetica', 10, 'bold'))
add_button.grid(row=9, column=0, columnspan=2, pady=10, sticky='ew')

# List frame
list_frame = tk.Frame(root)
list_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
list_frame.grid_columnconfigure(0, weight=1)

inventory_listbox = tk.Listbox(list_frame)
inventory_listbox.grid(row=0, column=0, sticky="nsew")

scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=inventory_listbox.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
inventory_listbox.config(yscrollcommand=scrollbar.set)

# Quit button frame at bottom-right
quit_frame = tk.Frame(root)
quit_frame.grid(row=3, column=1, sticky='se', padx=10, pady=10)

quit_button = tk.Button(quit_frame, text="Quit", command=quit_application, 
                       font=('Helvetica', 10, 'bold'), width=10)
quit_button.pack()

# Grid weights
root.grid_rowconfigure(0, weight=0)  # Header
root.grid_rowconfigure(1, weight=1)  # Form
root.grid_rowconfigure(2, weight=2)  # List
root.grid_rowconfigure(3, weight=0)  # Quit button
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Initialize
update_inventory_list()
configure_responsive_grid()
root.bind('<Configure>', lambda e: configure_responsive_grid())
update_clock()

# Handle window close button
root.protocol("WM_DELETE_WINDOW", quit_application)

root.mainloop()