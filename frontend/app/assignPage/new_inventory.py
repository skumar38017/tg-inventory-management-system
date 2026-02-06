# frontend/app/assignPage/new_inventory.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.assign_inventory_api_request import (
    submit_assigned_inventory,
    update_assigned_inventory,
    get_assigned_inventory_by_id,
    delete_assigned_inventory
)
from widgets.inventory_combobox import InventoryComboBox
from assignPage.edit_update import EditUpdateSection

class NewInventorySection:
    def __init__(self, parent_window, parent_instance):
        self.window = parent_window
        self.parent = parent_instance
        
        # Create edit/update section
        self.edit_update_section = EditUpdateSection(parent_window, parent_instance)
        
    def create_new_entry_section(self, content_frame):
        """Create the NEW ENTRY section"""
        # NEW ENTRY section
        new_entry_frame = tk.LabelFrame(content_frame, text="NEW ENTRY", 
                                    font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.qr_barcode_header_font_size, 'bold'))
        new_entry_frame.grid(row=2, column=0, sticky="nsew")
        new_entry_frame.grid_columnconfigure(0, weight=1)
        new_entry_frame.grid_rowconfigure(0, weight=1)  # For the treeview
        
        # Treeview for new entries
        self.parent.new_entry_tree = ttk.Treeview(new_entry_frame)
        self.parent.new_entry_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars - Modified for proper left-to-right scrolling
        new_entry_vsb = ttk.Scrollbar(new_entry_frame, orient="vertical", command=self.parent.new_entry_tree.yview)
        new_entry_hsb = ttk.Scrollbar(new_entry_frame, orient="horizontal", command=self.parent.new_entry_tree.xview)
        self.parent.new_entry_tree.configure(yscrollcommand=new_entry_vsb.set, xscrollcommand=new_entry_hsb.set)
        
        # Grid placement
        new_entry_vsb.grid(row=0, column=1, sticky="ns")
        new_entry_hsb.grid(row=1, column=0, sticky="ew")
            
        # Action buttons frame for the new entry section
        action_frame = tk.Frame(new_entry_frame)
        action_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # Edit button
        edit_btn = tk.Button(action_frame, text="Edit", command=self.edit_update_section.edit_selected_entry,
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size))
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Update button
        update_btn = tk.Button(action_frame, text="Update", command=self.edit_update_section.update_selected_entry,
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size))
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_btn = tk.Button(action_frame, text="Delete", command=self.edit_update_section.delete_selected_entry,
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size))
        delete_btn.pack(side=tk.LEFT, padx=5)

        return new_entry_frame
    
    # Delegate methods to edit_update section
    def edit_selected_entry(self):
        """Delegate to edit_update section"""
        self.edit_update_section.edit_selected_entry()
    
    def update_selected_entry(self):
        """Delegate to edit_update section"""
        self.edit_update_section.update_selected_entry()
    
    def delete_selected_entry(self):
        """Delegate to edit_update section"""
        self.edit_update_section.delete_selected_entry()
    
    # --------------------------- New Entry Popup ---------------------------
    def new_entry(self):
        """Create a centered form-style popup window with larger input boxes and date pickers"""
        # Create popup window
        popup = tk.Toplevel(self.window)
        popup.title("Register New Assignment")
        
        # Make the popup modal
        popup.grab_set()
        
        # Window dimensions (larger for better fit with increased fonts and buttons)
        popup.geometry("1200x900")  # Increased width to accommodate larger fonts and buttons
        popup.minsize(1000, 800)
        
        # Header
        header_frame = tk.Frame(popup, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, pady=10)
        tk.Label(header_frame, text="NEW INVENTORY ASSIGNMENT", 
                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.qr_barcode_header_font_size, 'bold'), bg="#f0f0f0").pack(pady=10)
        
        # Main content area with scrollbar
        container = tk.Frame(popup)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="center")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            if scrollable_frame.winfo_reqwidth() < canvas.winfo_width():
                canvas.itemconfig(1, width=canvas.winfo_width())
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        # Field definitions
        fields = [
            ("assign_to", "Assigned To:"),
            ("employee_name", "Employee Name:"),
            ("sno", "SNo:"),
            ("zone_activity", "Zone Activity:"),
            ("inventory_id", "Inventory ID:"),
            ("project_id", "Project ID:"),
            ("product_id", "Product ID:"),
            ("inventory_name", "Inventory Name:"),
            ("description", "Description:"),
            ("quantity", "Quantity:"),
            ("status", "Status:"),
            ("purpose_reason", "Purpose/Reason:"),
            ("assigned_date", "Assigned Date:"),
            ("assign_by", "Assigned By:"),
            ("assignment_return_date", "Return Date:"),
            ("comment", "Comments:")
        ]
        
        # Store all entry widgets for each row
        all_entries = []
# ---------------------------------------------- Create Form ----------------------------------------------------------    
        def create_form_row(parent_frame):
            entries = {}
            
            # Create a frame for this form row with 2 columns
            form_row_frame = tk.Frame(parent_frame)
            form_row_frame.pack(fill=tk.X, pady=10)
            
            # Configure grid weights for responsive layout
            form_row_frame.grid_columnconfigure(0, weight=1)
            form_row_frame.grid_columnconfigure(1, weight=1)
            
            # Split fields into two columns (8 fields each)
            left_fields = fields[:8]   # First 8 fields in left column (without Description)
            right_fields = fields[8:]  # Remaining 9 fields in right column (including Description)
            
            # Create left column
            left_frame = tk.Frame(form_row_frame)
            left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            
            # Create right column  
            right_frame = tk.Frame(form_row_frame)
            right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            
            def create_field_widget(parent_frame, row_index, field_name, label_text):
                """Helper function to create individual field widgets"""
                # Label with universal font
                lbl = tk.Label(parent_frame, text=label_text, anchor='e', padx=5,
                              font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold'))
                lbl.grid(row=row_index, column=0, sticky='e', pady=3)
                
                if field_name in ["assigned_date", "assignment_return_date"]:
                    # DateEntry for date fields
                    date_frame = tk.Frame(parent_frame)
                    date_frame.grid(row=row_index, column=1, sticky='ew', pady=3)
                    
                    entry = DateEntry(
                        date_frame,
                        width=universal_font_box_size.search_entry_width,
                        background='darkblue',
                        foreground='white',
                        borderwidth=2,
                        date_pattern='yyyy-mm-dd',
                        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.date_box_size),
                        calendar_font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.date_box_size),
                        calendar_width=universal_font_box_size.ID * 10,
                        calendar_height=universal_font_box_size.ID * 10
                    )
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    
                    if field_name == "assigned_date":
                        entry.set_date(date.today())
                    elif field_name == "assignment_return_date":
                        entry.set_date(date.today() + timedelta(days=15))
                elif field_name == "status":
                    # Combobox for status
                    status_frame = tk.Frame(parent_frame)
                    status_frame.grid(row=row_index, column=1, sticky='ew', pady=3)
                    
                    status_combo = ttk.Combobox(
                        status_frame,
                        values=self.parent.status_options,
                        state="readonly",
                        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                        width=universal_font_box_size.search_entry_width,
                        height=15  # Increased dropdown height to show more options
                    )
                    # Configure dropdown list font
                    status_combo.option_add('*TCombobox*Listbox.Font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
                    status_combo.set("Assigned")
                    status_combo.pack(fill=tk.X, expand=True, ipady=4)  # Increased ipady for better height match
                    entries[field_name] = status_combo
                elif field_name == "inventory_name":
                    # InventoryComboBox for inventory name
                    combo_frame = tk.Frame(parent_frame)
                    combo_frame.grid(row=row_index, column=1, sticky='ew', pady=3)
                    
                    entry = InventoryComboBox(combo_frame,
                                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                                            width=universal_font_box_size.search_entry_width,
                                            height=universal_font_box_size.new_entry_header_height)
                    entry.pack(fill=tk.X, expand=True, ipady=4)
                    
                    # Bind selection to update related fields
                    entry.bind('<<ComboboxSelected>>', 
                            lambda e: self._update_inventory_fields(entries, e))
                    entries[field_name] = entry
                else:
                    # Regular Entry for other fields with universal font
                    entry = tk.Entry(parent_frame, borderwidth=1, relief="solid", 
                                   width=universal_font_box_size.search_entry_width,
                                   font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
                    entry.grid(row=row_index, column=1, sticky='ew', pady=3, ipady=4)
                    
                    if field_name == "quantity":
                        entry.insert(0, "1")
                    
                    entries[field_name] = entry
            
            # Process left column fields
            for i, (field_name, label_text) in enumerate(left_fields):
                create_field_widget(left_frame, i, field_name, label_text)
            
            # Process right column fields
            for i, (field_name, label_text) in enumerate(right_fields):
                create_field_widget(right_frame, i, field_name, label_text)
            
            # Add separator line at the end of fields
            separator_frame = tk.Frame(form_row_frame)
            separator_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 5))
            
            separator = ttk.Separator(separator_frame, orient='horizontal')
            separator.pack(fill=tk.X, expand=True)
            
            return entries
        
        def _create_field_widget(self, parent_frame, row_index, field_name, label_text, entries):
            """Helper method to create individual field widgets"""
            # Label with universal font
            lbl = tk.Label(parent_frame, text=label_text, anchor='e', padx=5,
                          font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold'))
            lbl.grid(row=row_index, column=0, sticky='e', pady=3)
            
            if field_name in ["assigned_date", "assignment_return_date"]:
                # DateEntry for date fields
                date_frame = tk.Frame(parent_frame)
                date_frame.grid(row=row_index, column=1, sticky='ew', pady=3)
                
                entry = DateEntry(
                    date_frame,
                    width=universal_font_box_size.search_entry_width,
                    background='darkblue',
                    foreground='white',
                    borderwidth=2,
                    date_pattern='yyyy-mm-dd',
                    font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.date_box_size),
                    calendar_font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.date_box_size),
                    calendar_width=universal_font_box_size.ID * 10,
                    calendar_height=universal_font_box_size.ID * 10
                )
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                if field_name == "assigned_date":
                    entry.set_date(date.today())
                elif field_name == "assignment_return_date":
                    entry.set_date(date.today() + timedelta(days=15))
            elif field_name == "status":
                # Combobox for status
                status_frame = tk.Frame(parent_frame)
                status_frame.grid(row=row_index, column=1, sticky='ew', pady=3)
                
                status_combo = ttk.Combobox(
                    status_frame,
                    values=self.parent.status_options,
                    state="readonly",
                    font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                    width=universal_font_box_size.search_entry_width,
                    height=universal_font_box_size.new_entry_header_height
                )
                # Configure dropdown list font
                status_combo.option_add('*TCombobox*Listbox.Font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
                status_combo.set("Assigned")
                status_combo.pack(fill=tk.X, expand=True, ipady=4)
                entries[field_name] = status_combo
            elif field_name == "inventory_name":
                # InventoryComboBox for inventory name
                combo_frame = tk.Frame(parent_frame)
                combo_frame.grid(row=row_index, column=1, sticky='ew', pady=3)
                
                entry = InventoryComboBox(combo_frame,
                                        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                                        width=universal_font_box_size.search_entry_width,
                                        height=universal_font_box_size.new_entry_header_height)
                entry.pack(fill=tk.X, expand=True, ipady=4)
                
                # Bind selection to update related fields
                entry.bind('<<ComboboxSelected>>', 
                        lambda e: self._update_inventory_fields(entries, e))
                entries[field_name] = entry
            else:
                # Regular Entry for other fields with universal font
                entry = tk.Entry(parent_frame, borderwidth=1, relief="solid", 
                               width=universal_font_box_size.search_entry_width,
                               font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
                entry.grid(row=row_index, column=1, sticky='ew', pady=3, ipady=4)
                
                if field_name == "quantity":
                    entry.insert(0, "1")
                
                entries[field_name] = entry
            
            return entries
                    
        # Create initial form (centered)
        form_frame = tk.Frame(scrollable_frame)
        form_frame.pack(pady=10)
        all_entries.append(create_form_row(form_frame))
        
        # Button functions
        def add_row():
            new_form_frame = tk.Frame(scrollable_frame)
            new_form_frame.pack(pady=10)
            all_entries.append(create_form_row(new_form_frame))
        
        def remove_row():
            if len(all_entries) > 1:
                all_entries.pop()
                scrollable_frame.winfo_children()[-1].destroy()
        
        def clear_form():
            for entries in all_entries:
                for field_name, entry in entries.items():
                    if field_name in ["assigned_date", "assignment_return_date"]:
                        if field_name == "assigned_date":
                            entry.set_date(date.today())
                        elif field_name == "assignment_return_date":
                            entry.set_date(date.today() + timedelta(days=15))
                    else:
                        entry.delete(0, tk.END)
                        # Restore defaults if needed
                        if field_name == "quantity":
                            entry.insert(0, "1")
                        elif field_name == "status":
                            entry.insert(0, "Assigned")

        def validate_assignment(assignment):
            required_fields = ['inventory_id', 'assign_to', 'employee_name']
            missing = [field for field in required_fields if not assignment.get(field)]
            if missing:
                messagebox.showwarning("Validation Error", 
                    f"Missing required fields: {', '.join(missing)}")
                return False
            return True
        
        def submit_data():
            data = {'assignments': []}
            
            for entries in all_entries:
                assignment = {}
                for field_name, entry in entries.items():
                    if field_name in ["assigned_date", "assignment_return_date"]:
                        # Get date from DateEntry widget
                        value = entry.get_date().strftime('%Y-%m-%d')
                    else:
                        value = entry.get()
                    
                    if value:
                        assignment[field_name] = value
                
                if assignment:
                    if not validate_assignment(assignment):
                        return
                    data['assignments'].append(assignment)
            
            if not data['assignments']:
                messagebox.showwarning("Warning", "No data to submit")
                return
            
            try:
                popup.config(cursor="watch")
                popup.update()
                
                success = submit_assigned_inventory(data)
                if success:
                    messagebox.showinfo("Success", f"{len(data['assignments'])} assignment(s) submitted")
                    self.parent.refresh_assigned_inventory_list()
                    self.parent.load_recent_submissions()
                    clear_form()
                else:
                    messagebox.showerror("Error", "Failed to submit assignment(s)")
            except Exception as e:
                messagebox.showerror("Error", f"Submission failed: {str(e)}")
            finally:
                popup.config(cursor="")
        
        # Button frame (centered)
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        
        buttons = [
            ("Add Row", add_row),
            ("Remove Row", remove_row),
            ("Clear", clear_form),
            ("Back", popup.destroy),
            ("Submit", submit_data)
        ]
        
        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command, 
                          width=universal_font_box_size.button_width,
                          font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Make submit button stand out
        button_frame.winfo_children()[-1].config(bg="#e0e0e0")
        
    def _update_inventory_fields(self, entries, event):
        """Update related fields when an inventory item is selected"""
        # Get the combobox widget that triggered the event
        combo_box = event.widget
        
        # Get the selected item data
        selected_item = combo_box.get_selected_item()
        if selected_item:
            # Update all relevant fields from the selected inventory item
            field_mappings = {
                'sno': 'sno',
                'inventory_id': 'inventory_id',
                'product_id': 'product_id',
                'project_id': 'project_id',
            }
            
            for field_name, item_key in field_mappings.items():
                if field_name in entries and item_key in selected_item:
                    entries[field_name].delete(0, tk.END)
                    entries[field_name].insert(0, str(selected_item[item_key]))
    
    #  ----------------------- End of New Entry Popup -----------------------
    
    def add_table_row(self):
        """Add a new row to the input table in the new entry tree with auto-generated ID"""
        # Generate default values for a new row
        default_values = [
            ""  # Auto-generated short  ID
            "",  # SNo
            "",  # Assigned To
            self.parent.employee_name.get() or "",  # Employee Name
            self.parent.inventory_id.get() or "",  # Inventory ID
            self.parent.project_id.get() or "",  # Project ID
            self.parent.product_id.get() or "",  # Product ID
            "",  # Inventory Name
            "",  # Description
            "1",  # Default quantity
            "Assigned",  # Default status
            datetime.now().strftime('%Y-%m-%d'),  # Assigned Date
            datetime.now().strftime('%Y-%m-%d'),  # Submission Date
            "",  # Purpose/Reason
            "",  # Assigned By
            "",  # Comments
            (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
            ""  # Assignment Barcode
        ]
        
        # Add the new row to the treeview
        self.parent.new_entry_tree.insert('', 'end', values=default_values)

    def remove_table_row(self):
        """Remove the selected row from the input table"""
        selected_item = self.parent.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a row to remove")
            return
            
        self.parent.new_entry_tree.delete(selected_item)

    def toggle_wrap(self):
        """Toggle between wrapped and original column sizes"""
        if not self.parent.is_wrapped:
            # Adjust columns to fit content
            for tree in [self.parent.assigned_tree, self.parent.recent_tree, self.parent.new_entry_tree]:
                for col in range(len(self.parent.headers)):
                    tree.column(col, width=0)  # Reset width
                    tree.column(col, stretch=True)  # Allow stretching
            self.parent.wrap_btn.config(text="Unwrap")
            self.parent.is_wrapped = True
        else:
            # Reset to original column widths
            for tree in [self.parent.assigned_tree, self.parent.recent_tree, self.parent.new_entry_tree]:
                for col in range(len(self.parent.headers)):
                    tree.column(col, width=100, stretch=False)
            self.parent.wrap_btn.config(text="Wrap")
            self.parent.is_wrapped = False

    def clear_all_entries(self):
        """Clear all form fields and entries"""
        if hasattr(self.parent, 'inventory_id'):
            self.parent.inventory_id.delete(0, tk.END)
        if hasattr(self.parent, 'project_id'):
            self.parent.project_id.delete(0, tk.END)
        if hasattr(self.parent, 'product_id'):
            self.parent.product_id.delete(0, tk.END)
        if hasattr(self.parent, 'employee_name'):
            self.parent.employee_name.delete(0, tk.END)
        if hasattr(self.parent, 'new_entry_tree'):
            self.parent.new_entry_tree.delete(*self.parent.new_entry_tree.get_children())
        
        self.parent.currently_editing_id = None
        self.parent.edit_mode = False
