# frontend/app/damage_inventory.py

from common_imports import *
from api_request.damage_inventory_api_request import (
    search_wastage_inventory_by_id,
    submit_wastage_inventory,
    update_wastage_inventory,
    delete_wastage_inventory,
    load_submitted_wastage_inventory,
    show_all_wastage_inventory
)

class DamageWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Inventory Damage/Waste Management")
        
        # Maximize window
        self.maximize_window()
        # Get status options from StatusEnum
        
        self.status_options = [status.value for status in StatusEnum]
        
        # Define the fields based on API schema
        self.fields = [
            "assign_to", "sno", "employee_name", "inventory_id", "project_id",
            "product_id", "inventory_name", "description", "quantity", "status",
            "receive_date", "receive_by", "check_status", "location", "project_name",
            "event_date", "comment", "zone_activity", "wastage_reason", "wastage_date",
            "wastage_approved_by", "wastage_status"
        ]
        
        self.display_names = [
            "Assign To", "S.No", "Employee Name", "Inventory ID", "Project ID",
            "Product ID", "Inventory Name", "Description", "Quantity", "Status",
            "Receive Date", "Receive By", "Check Status", "Location", "Project Name",
            "Event Date", "Comment", "Zone/Activity", "Wastage Reason", "Wastage Date",
            "Approved By", "Wastage Status"
        ]
        
        # Variables for edit functionality
        self.edit_mode = False
        self.current_edit_id = None
        self.current_edit_employee = None
            
        # Data storage for comboboxes
        self.inventory_data = []
        self.project_data = []
        self.entries = {}  # Initialize entries dictionary
        
        # Hide parent window (optional)
        self.parent.withdraw()

        # Setup the UI
        self.setup_ui()
            
        # Load initial data
        self.refresh_data()

        # Focus on this window
        self.window.focus_set()
        
        logger.info("Damage/Waste Management window opened successfully")

    def maximize_window(self):
        maximize_window(self.window)

    def setup_ui(self):
        """Set up all UI elements"""
        # Main container
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = tk.LabelFrame(main_frame, text="Enter Wastage Details", padx=5, pady=5)
        input_frame.pack(fill=tk.X, pady=5)
        
        # Create input fields
        self.entries = {}
        for i, (field, display) in enumerate(zip(self.fields, self.display_names)):
            row = i // 3
            col = (i % 3) * 2
            
            tk.Label(input_frame, text=display + ":").grid(row=row, column=col, sticky=tk.E, padx=5, pady=2)
            
            # Special handling for inventory_name and project_name
            if field == "inventory_name":
                self.inventory_name_combobox = InventoryComboBox(
                    input_frame, 
                    width=23
                )
                self.inventory_name_combobox.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
                self.inventory_name_combobox.bind("<<ComboboxSelected>>", self.on_inventory_selected)
                self.entries[field] = self.inventory_name_combobox
                
            elif field == "project_name":
                self.project_name_combobox = ttk.Combobox(
                    input_frame, 
                    width=23,
                    postcommand=self.update_project_combobox
                )
                self.project_name_combobox.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
                self.project_name_combobox.bind("<<ComboboxSelected>>", self.on_project_selected)
                self.entries[field] = self.project_name_combobox
                
            # Use Combobox for status and wastage_status fields
            elif field in ["status", "wastage_status", "check_status"]:
                combo = ttk.Combobox(input_frame, width=23, values=self.status_options)
                combo.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
                self.entries[field] = combo
                
            # Use DateEntry for date fields
            elif field in ["wastage_date", "event_date", "receive_date"]:
                date_entry = DateEntry(input_frame, width=22, background='darkblue',
                                      foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                date_entry.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
                self.entries[field] = date_entry
                
            else:
                entry = tk.Entry(input_frame, width=25)
                entry.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
                self.entries[field] = entry
            
            # Set default values for certain fields
            if field == "wastage_date":
                self.entries[field].set_date(datetime.now().date())
            elif field == "status":
                self.entries[field].set("damaged")
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Action buttons
        tk.Button(button_frame, text="New", command=self.new_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Submit", command=self.submit_form).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update", command=self.update_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = tk.LabelFrame(main_frame, text="Search", padx=5, pady=5)
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Inventory ID:").grid(row=0, column=0, sticky=tk.E, padx=5)
        self.search_inventory_id = tk.Entry(search_frame, width=20)
        self.search_inventory_id.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        tk.Label(search_frame, text="Project ID:").grid(row=0, column=2, sticky=tk.E, padx=5)
        self.search_project_id = tk.Entry(search_frame, width=20)
        self.search_project_id.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        tk.Label(search_frame, text="Product ID:").grid(row=0, column=4, sticky=tk.E, padx=5)
        self.search_product_id = tk.Entry(search_frame, width=20)
        self.search_product_id.grid(row=0, column=5, sticky=tk.W, padx=5)
        
        tk.Button(search_frame, text="Search", command=self.search_inventory).grid(row=0, column=6, padx=5)
        
        # Results frame with treeview
        results_frame = tk.LabelFrame(main_frame, text="Results", padx=5, pady=5)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview with scrollbars
        self.tree = ttk.Treeview(results_frame, columns=self.display_names, show="headings")
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure column headings
        for col, name in enumerate(self.display_names):
            self.tree.heading(col, text=name)
            self.tree.column(col, width=120, minwidth=50)
        
        # Bind treeview selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Return button
        return_btn = tk.Button(button_frame, text="Return to Main", command=self.on_close,
                             font=('Helvetica', 12, 'bold'))
        return_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configure grid weights
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

    def update_inventory_combobox(self):
        """Update inventory_name combobox with data from API"""
        try:
            # Get inventory data from API
            self.inventory_data = show_all_wastage_inventory() or []
            inventory_names = list({item.get('inventory_name', '') for item in self.inventory_data if item.get('inventory_name')})
            self.inventory_name_combobox['values'] = inventory_names
        except Exception as e:
            logger.error(f"Error updating inventory combobox: {str(e)}")
            messagebox.showerror("Error", "Failed to load inventory names")

    def on_inventory_selected(self, event):
        """Auto-fill fields when inventory name is selected"""
        selected_item = self.inventory_name_combobox.get_selected_item()
        if not selected_item:
            return
            
        # Auto-fill related fields
        fields_to_fill = {
            'product_id': selected_item.get('product_id', ''),
            'sno': selected_item.get('sno', ''),
            'inventory_id': selected_item.get('inventory_id', ''),
            'project_id': selected_item.get('project_id', ''),
            'description': selected_item.get('description', ''),
            'quantity': selected_item.get('quantity', ''),
            'location': selected_item.get('location', ''),
            'employee_name': selected_item.get('employee_name', ''),
            'assign_to': selected_item.get('assign_to', ''),
            'status': selected_item.get('status', ''),
            'zone_activity': selected_item.get('zone_activity', '')
        }
        
        for field, value in fields_to_fill.items():
            if field in self.entries:
                if isinstance(self.entries[field], ttk.Combobox):
                    self.entries[field].set(value)
                elif isinstance(self.entries[field], DateEntry):
                    try:
                        if value:  # Only try to set date if there's a value
                            date_val = datetime.strptime(value, "%Y-%m-%d").date()
                            self.entries[field].set_date(date_val)
                    except (ValueError, AttributeError):
                        pass
                else:
                    self.entries[field].delete(0, tk.END)
                    self.entries[field].insert(0, value)
    
        # Update project combobox with related projects
        self.update_project_combobox()

    def update_project_combobox(self):
        """Update project_name combobox with projects related to selected inventory"""
        try:
            # Get currently selected inventory item
            selected_inventory = self.inventory_name_combobox.get_selected_item()
            
            if selected_inventory:
                # Get all inventory data from combobox
                all_inventory = self.inventory_name_combobox.get_all_inventory_data()
                
                # Filter projects that match the selected inventory's product_id or inventory_id
                related_projects = []
                for item in all_inventory:
                    # Match by product_id if available, otherwise by inventory_id
                    if (selected_inventory.get('product_id') and 
                        item.get('product_id') == selected_inventory.get('product_id')):
                        related_projects.append(item)
                    elif (selected_inventory.get('inventory_id') and 
                        item.get('inventory_id') == selected_inventory.get('inventory_id')):
                        related_projects.append(item)
                
                # Extract unique project names
                project_names = list({item.get('project_name', '') 
                                    for item in related_projects 
                                    if item.get('project_name')})
                
                self.project_name_combobox['values'] = project_names
            else:
                # If no inventory selected, show all projects
                self.project_data = show_all_wastage_inventory() or []
                project_names = list({item.get('project_name', '') 
                                    for item in self.project_data 
                                    if item.get('project_name')})
                self.project_name_combobox['values'] = project_names
                
        except Exception as e:
            logger.error(f"Error updating project combobox: {str(e)}")
            messagebox.showerror("Error", "Failed to load related projects")

    def on_project_selected(self, event):
        """Auto-fill fields when project name is selected"""
        selected_name = self.project_name_combobox.get()
        if not selected_name:
            return
            
        # Get currently selected inventory item
        selected_inventory = self.inventory_name_combobox.get_selected_item()
        
        if not selected_inventory:
            return
            
        # Find the selected project that matches both project_name and inventory criteria
        all_inventory = self.inventory_name_combobox.get_all_inventory_data()
        
        selected_project = None
        for item in all_inventory:
            if (item.get('project_name') == selected_name and 
                ((selected_inventory.get('product_id') and 
                item.get('product_id') == selected_inventory.get('product_id')) or
                (selected_inventory.get('inventory_id') and 
                item.get('inventory_id') == selected_inventory.get('inventory_id')))):
                selected_project = item
                break
        
        if selected_project:
            # Auto-fill related fields
            fields_to_fill = {
                'project_name': selected_project.get('project_name'),
                'project_id': selected_project.get('project_id', ''),
                'event_date': selected_project.get('event_date', ''),
                'location': selected_project.get('location', ''),
                'zone_activity': selected_project.get('zone_activity', '')
            }
            
            for field, value in fields_to_fill.items():
                if field in self.entries:
                    if isinstance(self.entries[field], ttk.Combobox):
                        self.entries[field].set(value)
                    elif isinstance(self.entries[field], DateEntry):
                        try:
                            if value:  # Only try to set date if there's a value
                                date_val = datetime.strptime(value, "%Y-%m-%d").date()
                                self.entries[field].set_date(date_val)
                        except (ValueError, AttributeError):
                            pass
                    else:
                        self.entries[field].delete(0, tk.END)
                        self.entries[field].insert(0, value)

    def new_entry(self):
        """Clear all fields for a new entry"""
        if self.edit_mode:
            if not messagebox.askyesno("Confirm", "Discard changes and create new entry?"):
                return
        
        self.clear_form_fields()
        
        self.edit_mode = False
        self.current_edit_id = None
        self.current_edit_employee = None
        
        logger.info("Prepared form for new entry")
        
        for field, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                widget.set('')
                widget.config(state='normal')
            elif isinstance(widget, DateEntry):
                widget.set_date(datetime.now().date())
                widget.config(state='normal')
            else:
                widget.config(state='normal')
                widget.delete(0, tk.END)
        
        # Set default values
        self.entries["wastage_date"].set_date(datetime.now().date())
        self.entries["status"].set("damaged")
        
        self.edit_mode = False
        self.current_edit_id = None
        self.current_edit_employee = None
        
        logger.info("Prepared form for new entry")

    def on_tree_select(self, event):
        """Handle selection from treeview"""
        selected = self.tree.focus()
        if not selected:
            return
            
        values = self.tree.item(selected, "values")
        if not values:
            return
        
        # Store the selected item ID for later reference
        self.selected_item = selected
        
        logger.info(f"Item selected: {values[self.fields.index('inventory_id')]}")

    def clear_form_fields(self):
        """Clear form fields without changing edit mode"""
        for field, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            elif isinstance(widget, DateEntry):
                widget.set_date(datetime.now().date())
            else:
                widget.delete(0, tk.END)
        
        # Set default values
        self.entries["wastage_date"].set_date(datetime.now().date())
        self.entries["status"].set("damaged")
    
    def edit_selected(self):
        """Edit the selected entry from the treeview"""
        if not hasattr(self, 'selected_item'):
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
            
        values = self.tree.item(self.selected_item, "values")
        if not values:
            return
            
        # Clear form fields without resetting edit mode
        self.clear_form_fields()
        
        # Populate fields with selected item
        for field, value in zip(self.fields, values):
            if isinstance(self.entries[field], ttk.Combobox):
                self.entries[field].set(value)
            elif isinstance(self.entries[field], DateEntry):
                try:
                    date_val = datetime.strptime(value, "%Y-%m-%d").date()
                    self.entries[field].set_date(date_val)
                except (ValueError, AttributeError):
                    pass
            else:
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, value)
        
        # Make read-only fields for fields that shouldn't be edited
        for field in ["inventory_id", "employee_name", "product_id", "project_id"]:
            self.entries[field].config(state='readonly')
            
        # Set edit mode
        self.edit_mode = True
        self.current_edit_id = values[self.fields.index("inventory_id")]
        self.current_edit_employee = values[self.fields.index("employee_name")]
        
        # Focus on the first editable field
        self.entries["assign_to"].focus_set()
        
        logger.info(f"Editing entry: {self.current_edit_id}")

    def refresh_data(self):
        """Refresh all data from API"""
        results = show_all_wastage_inventory()
        self.display_results(results)
        
        # Also update our stored data for comboboxes
        self.inventory_data = results or []
        self.project_data = results or []
        
        logger.info("Data refreshed")

    def display_results(self, results):
        """Display results in treeview"""
        self.tree.delete(*self.tree.get_children())
        
        if not results:
            return
            
        for item in results:
            values = [item.get(field, "") for field in self.fields]
            self.tree.insert("", tk.END, values=values)

    def search_inventory(self):
        """Search inventory based on criteria"""
        inventory_id = self.search_inventory_id.get().strip()
        project_id = self.search_project_id.get().strip()
        product_id = self.search_product_id.get().strip()
        
        results = search_wastage_inventory_by_id(
            inventory_id=inventory_id,
            project_id=project_id,
            product_id=product_id
        )
        
        self.display_results(results)
        logger.info(f"Search completed with {len(results) if results else 0} results")

    def submit_form(self):
        """Submit new entry"""
        if self.edit_mode:
            return self.update_selected()
        
        # Prepare data from form
        data = {}
        for field, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                data[field] = widget.get().strip()
            elif isinstance(widget, DateEntry):
                data[field] = widget.get_date().strftime("%Y-%m-%d")
            else:
                data[field] = widget.get().strip()
        
        # Validate required fields
        if not data["inventory_id"] or not data["employee_name"]:
            messagebox.showwarning("Warning", "Inventory ID and Employee Name are required")
            return
        
        # Submit to API
        success = submit_wastage_inventory({"wastages": [data]})
        
        if success:
            messagebox.showinfo("Success", "Entry submitted successfully")
            self.new_entry()
            self.refresh_data()
        else:
            messagebox.showerror("Error", "Failed to submit entry")

    def update_selected(self):
        if not self.edit_mode or not self.current_edit_id or not self.current_edit_employee:
            messagebox.showwarning("Warning", "No item selected for editing")
            return
        
        # Prepare update data (only updatable fields)
        update_data = {
            "assign_to": self.entries["assign_to"].get().strip(),
            "sno": self.entries["sno"].get().strip(),
            "description": self.entries["description"].get().strip(),
            "quantity": self.entries["quantity"].get().strip(),
            "status": self.entries["status"].get().strip(),
            "receive_date": self.entries["receive_date"].get_date().strftime("%Y-%m-%d"),
            "receive_by": self.entries["receive_by"].get().strip(),
            "check_status": self.entries["check_status"].get().strip(),
            "location": self.entries["location"].get().strip(),
            "project_name": self.entries["project_name"].get().strip(),
            "comment": self.entries["comment"].get().strip(),
            "zone_activity": self.entries["zone_activity"].get().strip(),
            "wastage_reason": self.entries["wastage_reason"].get().strip(),
            "wastage_date": self.entries["wastage_date"].get_date().strftime("%Y-%m-%d"),
            "wastage_approved_by": self.entries["wastage_approved_by"].get().strip(),
            "wastage_status": self.entries["wastage_status"].get().strip()
        }
        
        # Call update API
        success = update_wastage_inventory(
            employee_name=self.current_edit_employee,
            inventory_id=self.current_edit_id,
            data=update_data
        )
        
        if success:
            messagebox.showinfo("Success", "Entry updated successfully")
            self.new_entry()
            self.refresh_data()
        else:
            messagebox.showerror("Error", "Failed to update entry")

    def delete_selected(self):
        """Delete selected entry"""
        if not hasattr(self, 'selected_item'):
            messagebox.showwarning("Warning", "No item selected")
            return
            
        values = self.tree.item(self.selected_item, "values")
        if not values:
            return
            
        employee_name = values[self.fields.index("employee_name")]
        inventory_id = values[self.fields.index("inventory_id")]
        
        if not messagebox.askyesno("Confirm", f"Delete entry {inventory_id}?"):
            return
        
        success = delete_wastage_inventory(
            employee_name=employee_name,
            inventory_id=inventory_id
        )
        
        if success:
            messagebox.showinfo("Success", "Entry deleted successfully")
            self.refresh_data()
        else:
            messagebox.showerror("Error", "Failed to delete entry")

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing Damage Inventory window")
        self.window.destroy()
        self.parent.deiconify()