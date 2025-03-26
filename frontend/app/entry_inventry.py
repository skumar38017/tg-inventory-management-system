# frontend/app/entry_inventry.py

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import time
import platform

from .inventory import fetch_inventory, add_inventory

def clear_fields():
    for entry in entries.values():
        if isinstance(entry, tk.Entry):
            entry.delete(0, tk.END)
    for var in checkbox_vars.values():
        var.set(False)

def update_inventory_list():
    inventory_listbox.delete(0, tk.END)
    inventory = fetch_inventory()
    for item in inventory:
        inventory_listbox.insert(tk.END, f"{item['S No']} | {item['Product ID']} | {item['Name']} | {item['Qty']} | {item['Purchase']} | {item['Purchase Price']} | {'Yes' if item['On Rent'] else 'No'} | {item['Vendor Name']} | {item['Total Rent']} | {'Yes' if item['On Event'] else 'No'} | {'Yes' if item['In Office'] else 'No'} | {'Yes' if item['In Warehouse'] else 'No'}")

def add_inventory_item():
    item = {}
    for key, widget in entries.items():
        if isinstance(widget, tk.Entry):
            value = widget.get()
            if not value and key in ['S No', 'Product ID', 'Name', 'Qty', 'Purchase', 'Purchase Price', 'Vendor Name', 'Total Rent']:
                messagebox.showerror("Error", f"{key.replace('_', ' ').title()} field is required")
                return
            if key in ['Qty', 'Purchase Price', 'Total Rent']:
                try:
                    item[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    messagebox.showerror("Error", f"{key.replace('_', ' ').title()} must be a number")
                    return
            else:
                item[key] = value
        elif isinstance(widget, tk.Checkbutton):
            item[key] = checkbox_vars[key].get()

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
    font_size = max(6, screen_width // 100)
    
    for label in labels.values():
        label.config(font=('Helvetica', font_size), anchor='w')
    for entry in entries.values():
        if isinstance(entry, tk.Entry):
            entry.config(font=('Helvetica', font_size), width=12)
    
    clock_label.config(font=('Helvetica', 8))
    company_label.config(font=('Helvetica', 7))

# Create the main window
root = tk.Tk()
root.title("Tagglabs's Inventory")

# Maximize window
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

# Header section
header_frame = tk.Frame(root)
header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

clock_label = tk.Label(header_frame, font=('Helvetica', 8))
clock_label.pack(pady=(0, 5))

company_frame = tk.Frame(header_frame)
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

# Form with horizontal scrolling
form_container = tk.Frame(root)
form_container.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

canvas = tk.Canvas(form_container)
scrollbar = tk.Scrollbar(form_container, orient="horizontal", command=canvas.xview)
scrollbar.pack(side="bottom", fill="x")
canvas.pack(side="top", fill="both", expand=True)
canvas.configure(xscrollcommand=scrollbar.set)

form_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=form_frame, anchor="nw")

# Field definitions in exact requested sequence
fields = [
    'S No', 'Product ID', 'Name', 'Qty', 
    'Purchase', 'Purchase Price', 'On Rent', 
    'Vendor Name', 'Total Rent', 'On Event', 
    'In Office', 'In Warehouse'
]

# Create labels and input fields
labels = {}
entries = {}
checkbox_vars = {}

for col, field in enumerate(fields):
    # Create label (left-aligned)
    label_text = field.replace('_', ' ').title()
    labels[field] = tk.Label(form_frame, text=label_text, font=('Helvetica', 15, 'bold'), anchor='w')
    
    # Create input widget
    if field in ['On Rent', 'On Event', 'In Office', 'In Warehouse']:
        checkbox_vars[field] = tk.BooleanVar()
        entries[field] = tk.Checkbutton(form_frame, variable=checkbox_vars[field])
    else:
        entries[field] = tk.Entry(form_frame, width=12)
    
    # Grid placement with proper alignment
    labels[field].grid(row=0, column=col, padx=5, pady=2, sticky='w')
    
    if field in ['On Rent', 'On Event', 'In Office', 'In Warehouse']:
        entries[field].grid(row=1, column=col, padx=5, pady=2)
    else:
        entries[field].grid(row=1, column=col, padx=5, pady=2, sticky='w')

# Update scroll region and set initial position to far left
form_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))
canvas.xview_moveto(0)  # This ensures scrolling starts from the leftmost position

# Bind to configure event to maintain left alignment when resizing
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.xview_moveto(0)  # Keep view locked to left after resizing

form_frame.bind("<Configure>", on_frame_configure)

# Buttons
button_frame = tk.Frame(root)
button_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)

add_button = tk.Button(button_frame, text="Add Item", command=add_inventory_item, 
                      font=('Helvetica', 10, 'bold'))
add_button.pack()

# List display
list_frame = tk.Frame(root)
list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
list_frame.grid_columnconfigure(0, weight=1)

inventory_listbox = tk.Listbox(list_frame)
inventory_listbox.grid(row=0, column=0, sticky="nsew")

list_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=inventory_listbox.yview)
list_scrollbar.grid(row=0, column=1, sticky="ns")
inventory_listbox.config(yscrollcommand=list_scrollbar.set)

# Quit button
quit_frame = tk.Frame(root)
quit_frame.grid(row=4, column=1, sticky='se', padx=10, pady=10)

quit_button = tk.Button(quit_frame, text="Quit", command=quit_application, 
                       font=('Helvetica', 10, 'bold'), width=10)
quit_button.pack()

# Grid configuration
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=0)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=0)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Initialize
update_inventory_list()
configure_responsive_grid()
root.bind('<Configure>', lambda e: configure_responsive_grid())
update_clock()
root.protocol("WM_DELETE_WINDOW", quit_application)

root.mainloop()