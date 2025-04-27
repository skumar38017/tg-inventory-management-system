#  frontend/app/entry_update_pop_window.py
from common_imports import *
from widgets.inventory_combobox import InventoryComboBox
from api_request.entry_inventory_api_request import (
    update_existing_inventory
)
from entry_inventory import update_main_inventory_list


class UpdatePopUpWindow:
    root = None
    def __init__(self, root_window):
        self.root = root_window
######################################################################################
#  Update Window with InventoryComboBox integration
######################################################################################
    @classmethod
    def create_update_button(cls, inventory_frame, root_window):
        """Create an Update button in the search frame"""
        cls.root = root_window  # Store the root window reference
        update_btn = tk.Button(
            inventory_frame,
            text="Update", 
            command=cls.open_update_window,
            font=('Helvetica', 9, 'bold')
        )
        return update_btn

    def clear_date_entry(date_entry):
        """Clear the date entry by setting it to empty and updating the display"""
        if date_entry['state'] == 'normal':  # Only clear if the field is editable
            # Clear the displayed text
            date_entry.delete(0, tk.END)
            # Clear the internal date value
            date_entry._set_text('')
            # For ttkbootstrap DateEntry, you might also need to reset the _date attribute
            if hasattr(date_entry, '_date'):
                date_entry._date = None

    def load_inventory_record(inventory_data):
        """Populate the form fields with inventory data"""
        if not inventory_data:
            return
            
        try:
            # Left column fields
            update_window_entries["Sno"].config(state='normal')
            update_window_entries["Sno"].delete(0, tk.END)
            update_window_entries["Sno"].insert(0, inventory_data.get('sno', ''))
            update_window_entries["Sno"].config(state='readonly')
            
            update_window_entries["ProductID"].config(state='normal')
            update_window_entries["ProductID"].delete(0, tk.END)
            update_window_entries["ProductID"].insert(0, inventory_data.get('product_id', ''))
            update_window_entries["ProductID"].config(state='readonly')
            
            update_window_entries["Material"].delete(0, tk.END)
            update_window_entries["Material"].insert(0, inventory_data.get('material', ''))
            
            update_window_entries["Manufacturer"].delete(0, tk.END)
            update_window_entries["Manufacturer"].insert(0, inventory_data.get('manufacturer', ''))
            
            # Handle dates - skip if empty
            purchase_date = inventory_data.get('purchase_date')
            if purchase_date:
                update_window_entries["Purchase Date"].set_date(purchase_date)
            else:
                UpdatePopUpWindow.clear_date_entry(update_window_entries["Purchase Date"])
                
            update_window_entries["Repair Quantity"].delete(0, tk.END)
            update_window_entries["Repair Quantity"].insert(0, inventory_data.get('repair_quantity', ''))
            
            update_window_entries["Vendor Name"].delete(0, tk.END)
            update_window_entries["Vendor Name"].insert(0, inventory_data.get('vendor_name', ''))
            
            update_window_entries["On Rent"].set(inventory_data.get('on_rent', False))
            
            returned_date = inventory_data.get('returned_date')
            if returned_date:
                update_window_entries["Returned Date"].set_date(returned_date)
            else:
                UpdatePopUpWindow.clear_date_entry(update_window_entries["Returned Date"])
                
            update_window_entries["In Office"].set(inventory_data.get('in_office', False))
            
            update_window_entries["Issued Qty"].delete(0, tk.END)
            update_window_entries["Issued Qty"].insert(0, inventory_data.get('issued_qty', ''))
            
            update_window_entries["Submitted By"].delete(0, tk.END)
            update_window_entries["Submitted By"].insert(0, inventory_data.get('submitted_by', ''))
            
            # Right column fields
            update_window_entries["InventoryID"].config(state='normal')
            update_window_entries["InventoryID"].delete(0, tk.END)
            update_window_entries["InventoryID"].insert(0, inventory_data.get('inventory_id', ''))
            update_window_entries["InventoryID"].config(state='readonly')
            
            update_window_entries["Name"].config(state='normal')
            update_window_entries["Name"].delete(0, tk.END)
            update_window_entries["Name"].insert(0, inventory_data.get('inventory_name', ''))
            update_window_entries["Name"].config(state='readonly')
            
            update_window_entries["Total Quantity"].delete(0, tk.END)
            update_window_entries["Total Quantity"].insert(0, inventory_data.get('total_quantity', ''))
            
            update_window_entries["Purchase Dealer"].delete(0, tk.END)
            update_window_entries["Purchase Dealer"].insert(0, inventory_data.get('purchase_dealer', ''))
            
            update_window_entries["Purchase Amount"].delete(0, tk.END)
            update_window_entries["Purchase Amount"].insert(0, inventory_data.get('purchase_amount', ''))
            
            update_window_entries["Repair Cost"].delete(0, tk.END)
            update_window_entries["Repair Cost"].insert(0, inventory_data.get('repair_cost', ''))
            
            update_window_entries["Total Rent"].delete(0, tk.END)
            update_window_entries["Total Rent"].insert(0, inventory_data.get('total_rent', ''))
            
            update_window_entries["Rented Returned"].set(inventory_data.get('rented_returned', False))
            
            update_window_entries["On Event"].set(inventory_data.get('on_event', False))
            
            update_window_entries["In Warehouse"].set(inventory_data.get('in_warehouse', False))
            
            update_window_entries["Balance Qty"].delete(0, tk.END)
            update_window_entries["Balance Qty"].insert(0, inventory_data.get('balance_qty', ''))
            
            # Additional information
            update_window_entries["ID"].config(state='normal')
            update_window_entries["ID"].delete(0, tk.END)
            update_window_entries["ID"].insert(0, inventory_data.get('id', ''))
            update_window_entries["ID"].config(state='readonly')
            
            update_window_entries["Updated At"].config(state='normal')
            update_window_entries["Updated At"].delete(0, tk.END)
            update_window_entries["Updated At"].insert(0, inventory_data.get('updated_at', ''))
            update_window_entries["Updated At"].config(state='readonly')
            
            update_window_entries["Unique Code"].config(state='normal')
            update_window_entries["Unique Code"].delete(0, tk.END)
            update_window_entries["Unique Code"].insert(0, inventory_data.get('inventory_unique_code', ''))
            update_window_entries["Unique Code"].config(state='readonly')
            
            update_window_entries["Created At"].config(state='normal')
            update_window_entries["Created At"].delete(0, tk.END)
            update_window_entries["Created At"].insert(0, inventory_data.get('created_at', ''))
            update_window_entries["Created At"].config(state='readonly')
            
            update_window_entries["Barcode"].config(state='normal')
            update_window_entries["Barcode"].delete(0, tk.END)
            update_window_entries["Barcode"].insert(0, inventory_data.get('inventory_barcode', ''))
            update_window_entries["Barcode"].config(state='readonly')
            
            update_window_entries["Barcode URL"].config(state='normal')
            update_window_entries["Barcode URL"].delete(0, tk.END)
            update_window_entries["Barcode URL"].insert(0, inventory_data.get('inventory_barcode_url', ''))
            update_window_entries["Barcode URL"].config(state='readonly')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory data: {str(e)}")

    @classmethod
    def open_update_window(cls):
        """Open the update inventory window with the specified layout"""
        if not cls.root:
            raise ValueError("Root window not set for UpdatePopUpWindow")
            
        update_window = tk.Toplevel(cls.root)
        update_window.title("Update Inventory")
        update_window.geometry("1000x800")
        
        # Main container
        main_frame = tk.Frame(update_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top section - Inventory Name dropdown and buttons
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(top_frame, text="Inventory Name:").pack(side='left', padx=5)
        
        # Use InventoryComboBox instead of regular Combobox
        inventory_name_combo = InventoryComboBox(top_frame, width=40)
        inventory_name_combo.pack(side='left', padx=5)
        
        # Load button
        load_btn = tk.Button(top_frame, text="Load Record", 
                            command=lambda: UpdatePopUpWindow.load_inventory_record(inventory_name_combo.get_selected_item()))
        load_btn.pack(side='left', padx=5)
        
        # Edit button - will enable editing of editable fields
        edit_btn = tk.Button(top_frame, text="Edit", 
                            command=lambda: toggle_edit_mode(True))
        edit_btn.pack(side='left', padx=5)
        
        # Middle section - Form fields
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Create two columns for the form
        left_column = tk.Frame(form_frame)
        left_column.pack(side='left', fill='both', expand=True, padx=5)
        
        right_column = tk.Frame(form_frame)
        right_column.pack(side='left', fill='both', expand=True, padx=5)
        
        # Dictionary to store all entry widgets for later access
        global update_window_entries
        update_window_entries = {}
        
        # Left column fields
        fields_left = [
            ("Sno:", "entry", True),  # Readonly
            ("ProductID:", "entry", True),  # Readonly
            ("Material:", "entry", False),
            ("Manufacturer:", "entry", False),
            ("Purchase Date:", "date", False),
            ("Repair Quantity:", "entry", False),
            ("Vendor Name:", "entry", False),
            ("On Rent:", "checkbox", False),
            ("Returned Date:", "date", False),
            ("In Office:", "checkbox", False),
            ("Issued Qty:", "entry", False),
            ("Submitted By:", "long_entry", False)
        ]
        
        for label_text, field_type, is_readonly in fields_left:
            frame = tk.Frame(left_column)
            frame.pack(fill='x', pady=2)
            
            tk.Label(frame, text=label_text, width=15, anchor='e').pack(side='left', padx=5)
            
            if field_type == "entry":
                entry = tk.Entry(frame)
                entry.config(state='readonly' if is_readonly else 'normal')
                entry.pack(side='left', fill='x', expand=True)
                update_window_entries[label_text.strip(":")] = entry
            elif field_type == "date":
                # Create a frame for date entry and clear button
                date_frame = tk.Frame(frame)
                date_frame.pack(side='left', fill='x', expand=True)  

                # Date entry
                date_entry = DateEntry(date_frame, date_pattern='yyyy-mm-dd')
                date_entry.pack(side='left', fill='x', expand=True)
                
                # Clear button for date
                clear_btn = tk.Button(
                    date_frame, 
                    text="Clear", 
                    command=lambda de=date_entry: UpdatePopUpWindow.clear_date_entry(de),
                    font=('Helvetica', 8),
                    state='normal'
                )
                clear_btn.pack(side='left', padx=2)
                
                # Store reference to the clear button
                date_entry.clear_btn = clear_btn
                
                # Initially disable the date entry
                date_entry.config(state='normal')
                
                update_window_entries[label_text.strip(":")] = date_entry

            elif field_type == "checkbox":
                var = tk.BooleanVar()
                cb = tk.Checkbutton(frame, variable=var)
                cb.pack(side='left')
                update_window_entries[label_text.strip(":")] = var
            elif field_type == "long_entry":
                entry = tk.Entry(frame)
                entry.config(state='normal')
                entry.pack(side='left', fill='x', expand=True)
                update_window_entries[label_text.strip(":")] = entry
        
        # Right column fields
        fields_right = [
            ("InventoryID:", "entry", True),  # Readonly
            ("Name:", "entry", True),        # Readonly
            ("Total Quantity:", "entry", False),
            ("Purchase Dealer:", "entry", False),
            ("Purchase Amount:", "entry", False),
            ("Repair Cost:", "entry", False),
            ("Total Rent:", "entry", False),
            ("Rented Returned:", "checkbox", False),
            ("On Event:", "checkbox", False),
            ("In Warehouse:", "checkbox", False),
            ("Balance Qty:", "entry", False)
        ]
        
        for label_text, field_type, is_readonly in fields_right:
            frame = tk.Frame(right_column)
            frame.pack(fill='x', pady=2)
            
            tk.Label(frame, text=label_text, width=15, anchor='e').pack(side='left', padx=5)
            
            if field_type == "entry":
                entry = tk.Entry(frame)
                entry.config(state='readonly' if is_readonly else 'normal')
                entry.pack(side='left', fill='x', expand=True)
                update_window_entries[label_text.strip(":")] = entry
            elif field_type == "checkbox":
                var = tk.BooleanVar()
                cb = tk.Checkbutton(frame, variable=var)
                cb.pack(side='left')
                update_window_entries[label_text.strip(":")] = var
        
        # Additional information section (read-only)
        info_frame = tk.LabelFrame(main_frame, text="Additional Information (Read-only or auto-generated)")
        info_frame.pack(fill='x', pady=10)
        
        # Create two columns for info section
        info_left = tk.Frame(info_frame)
        info_left.pack(side='left', fill='both', expand=True, padx=5)
        
        info_right = tk.Frame(info_frame)
        info_right.pack(side='left', fill='both', expand=True, padx=5)
        
        # Info fields left
        info_fields_left = [
            ("ID:", "entry", True),
            ("Updated At:", "entry", True),
            ("Unique Code:", "entry", True)
        ]
        
        for label_text, field_type, is_readonly in info_fields_left:
            frame = tk.Frame(info_left)
            frame.pack(fill='x', pady=2)
            
            tk.Label(frame, text=label_text, width=15, anchor='e').pack(side='left', padx=5)
            entry = tk.Entry(frame, state='readonly')
            entry.pack(side='left', fill='x', expand=True)
            update_window_entries[label_text.strip(":")] = entry
        
        # Info fields right
        info_fields_right = [
            ("Created At:", "entry", True),
            ("Barcode:", "entry", True),
            ("Barcode URL:", "entry", True)
        ]
        
        for label_text, field_type, is_readonly in info_fields_right:
            frame = tk.Frame(info_right)
            frame.pack(fill='x', pady=2)
            
            tk.Label(frame, text=label_text, width=15, anchor='e').pack(side='left', padx=5)
            entry = tk.Entry(frame, state='readonly')
            entry.pack(side='left', fill='x', expand=True)
            update_window_entries[label_text.strip(":")] = entry
        
        # Button section
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        buttons = [
            ("Clear", lambda: clear_form()),
            ("Update", lambda: update_inventory_record()),
            ("Close", update_window.destroy),
            ("Refresh", lambda: inventory_name_combo._load_all_inventory_names())
        ]
        
        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command).pack(side='left', padx=5, expand=True)
        
        def clear_form():
            """Clear all form fields while maintaining readonly states"""
            for key, widget in update_window_entries.items():
                if isinstance(widget, tk.Entry):
                    # Temporarily enable to clear, then restore state
                    current_state = widget['state']
                    widget.config(state='normal')
                    widget.delete(0, tk.END)
                    widget.config(state=current_state)
                elif isinstance(widget, DateEntry):
                    UpdatePopUpWindow.clear_date_entry(widget)
                    # Restore the state
                    if key in ["Purchase Date", "Returned Date"]:
                        widget.config(state='enable')
                        if hasattr(widget, 'clear_btn'):
                            widget.clear_btn.config(state='enable')
                elif isinstance(widget, tk.BooleanVar):
                    widget.set(False)
            
            inventory_name_combo.set('')
            toggle_edit_mode(False)
        
        def update_inventory_record():
            """Update the inventory record with form data"""
            try:
                # Get inventory ID - required field
                inventory_id = update_window_entries["InventoryID"].get()
                if not inventory_id:
                    messagebox.showerror("Error", "Inventory ID is required")
                    return

                # Collect data from form fields
                inventory_data = {
                    "inventory_id": inventory_id,
                    "inventory_name": update_window_entries["Name"].get(),
                    "material": update_window_entries["Material"].get(),
                    "total_quantity": update_window_entries["Total Quantity"].get(),
                    "manufacturer": update_window_entries["Manufacturer"].get(),
                    "purchase_dealer": update_window_entries["Purchase Dealer"].get(),
                    "purchase_date": update_window_entries["Purchase Date"].get(),
                    "purchase_amount": update_window_entries["Purchase Amount"].get(),
                    "repair_quantity": update_window_entries["Repair Quantity"].get(),
                    "repair_cost": update_window_entries["Repair Cost"].get(),
                    "on_rent": update_window_entries["On Rent"].get(),
                    "vendor_name": update_window_entries["Vendor Name"].get(),
                    "total_rent": update_window_entries["Total Rent"].get(),
                    "rented_inventory_returned": update_window_entries["Rented Returned"].get(),
                    "returned_date": update_window_entries["Returned Date"].get(),
                    "on_event": update_window_entries["On Event"].get(),
                    "in_office": update_window_entries["In Office"].get(),
                    "in_warehouse": update_window_entries["In Warehouse"].get(),
                    "issued_qty": update_window_entries["Issued Qty"].get(),
                    "balance_qty": update_window_entries["Balance Qty"].get(),
                    "submitted_by": update_window_entries["Submitted By"].get(),
                    "created_at": update_window_entries["Created At"].get()
                }

                # Call the update function
                updated_item = update_existing_inventory(inventory_data)
                
                # Show success message and clear the form
                messagebox.showinfo("Success", "Inventory record updated successfully")
                clear_form()  # Clear the form instead of reloading
                update_main_inventory_list()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update inventory: {str(e)}")

        def toggle_edit_mode(enable):
            """Toggle edit mode for editable fields"""
            # These fields should ALWAYS be readonly
            permanent_readonly_fields = [
                "Sno", "ProductID", "InventoryID", "Name", 
                "ID", "Updated At", "Unique Code", 
                "Created At", "Barcode", "Barcode URL"
            ]
            
            # These fields should be editable in edit mode
            editable_fields = [
                "Material", "Manufacturer", "Purchase Date", "Repair Quantity",
                "Vendor Name", "On Rent", "Returned Date", "In Office", "Issued Qty",
                "Submitted By", "Total Quantity", "Purchase Dealer", "Purchase Amount",
                "Repair Cost", "Total Rent", "Rented Returned", "On Event", 
                "In Warehouse", "Balance Qty"
            ]
            
            # Set permanent readonly fields
            for field in permanent_readonly_fields:
                if field in update_window_entries:
                    widget = update_window_entries[field]
                    if isinstance(widget, (tk.Entry, DateEntry)):
                        widget.config(state='readonly')
                    if hasattr(widget, 'clear_btn'):
                        widget.clear_btn.config(state='disabled')
            
            # Toggle editable fields
            for field in editable_fields:
                if field in update_window_entries:
                    widget = update_window_entries[field]
                    if isinstance(widget, tk.Entry):
                        widget.config(state='normal' if enable else 'readonly')
                    elif isinstance(widget, DateEntry):
                        widget.config(state='normal' if enable else 'disabled')
                        if hasattr(widget, 'clear_btn'):
                            widget.clear_btn.config(state='normal' if enable else 'disabled')
                    elif isinstance(widget, tk.BooleanVar):
                        pass  # Checkboxes are always editable

        # Initialize edit mode to False
        toggle_edit_mode(False)
        
        # Load initial inventory names
        inventory_name_combo._load_all_inventory_names()
        
        # Bind combobox selection to load record automatically
        inventory_name_combo.bind("<<ComboboxSelected>>", 
                                lambda e: UpdatePopUpWindow.load_inventory_record(inventory_name_combo.get_selected_item()))

################################################################################################################
