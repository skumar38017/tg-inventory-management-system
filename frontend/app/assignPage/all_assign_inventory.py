# frontend/app/assignPage/all_assign_inventory.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.assign_inventory_api_request import show_all_assigned_inventory_from_db

class AllAssignedInventorySection:
    def __init__(self, parent_window, parent_instance):
        self.window = parent_window
        self.parent = parent_instance
        
    def create_all_assigned_inventory_section(self, content_frame):
        """Create the ALL ASSIGNED INVENTORY section"""
        # ALL ASSIGNED INVENTORY section
        assigned_frame = tk.LabelFrame(content_frame, text="ALL ASSIGNED INVENTORY", 
                                     font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.qr_barcode_header_font_size, 'bold'))
        assigned_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        assigned_frame.grid_columnconfigure(0, weight=1)
        assigned_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview for assigned inventory
        self.parent.assigned_tree = ttk.Treeview(assigned_frame)
        self.parent.assigned_tree.grid(row=0, column=0, sticky="nsew")
            
        # Scrollbars - Modified for proper left-to-right scrolling
        assigned_vsb = ttk.Scrollbar(assigned_frame, orient="vertical", command=self.parent.assigned_tree.yview)
        assigned_hsb = ttk.Scrollbar(assigned_frame, orient="horizontal", command=self.parent.assigned_tree.xview)
        self.parent.assigned_tree.configure(yscrollcommand=assigned_vsb.set, xscrollcommand=assigned_hsb.set)
        
        # Grid placement - ensure horizontal scrollbar is at the bottom
        assigned_vsb.grid(row=0, column=1, sticky="ns")
        assigned_hsb.grid(row=1, column=0, sticky="ew")

        # Bind double-click events
        self.parent.assigned_tree.bind('<Double-1>', lambda e: self.load_selected_to_new_entry())

        return assigned_frame
    
    def load_selected_to_new_entry(self):
        """Load selected item from assigned tree into new entry tree"""
        selected_item = self.parent.assigned_tree.selection()
        if not selected_item:
            return
            
        try:
            item = selected_item[0]
            values = self.parent.assigned_tree.item(item, 'values')
            
            # Clear existing entries in new entry tree
            self.parent.new_entry_tree.delete(*self.parent.new_entry_tree.get_children())
            
            # Add the selected record to new entry tree
            self.parent.new_entry_tree.insert('', 'end', values=values)
            
            # Store the ID of the record being edited
            self.parent.currently_editing_id = values[0]
            self.parent.edit_mode = True
            
            # Update search fields
            self.parent.inventory_id.delete(0, tk.END)
            self.parent.inventory_id.insert(0, values[4])  # Inventory ID
            
            self.parent.project_id.delete(0, tk.END)
            self.parent.project_id.insert(0, values[5])  # Project ID
            
            self.parent.product_id.delete(0, tk.END)
            self.parent.product_id.insert(0, values[6])  # Product ID
            
            self.parent.employee_name.delete(0, tk.END)
            self.parent.employee_name.insert(0, values[3])  # Employee Name
                        
        except Exception as e:
            logger.error(f"Error loading selected item: {e}")
            messagebox.showerror("Error", "Failed to load selected item")
    
    def refresh_assigned_inventory_list(self):
        """Refresh the list of all assigned inventory with proper column sizing"""
        try:
            # Clear existing items
            self.parent.assigned_tree.delete(*self.parent.assigned_tree.get_children())
            
            # Load data from database
            inventory_list = show_all_assigned_inventory_from_db()
            
            if not inventory_list:
                return
            
            # Add items to treeview
            for item in inventory_list:
                values = [
                    item.get('id', ''),
                    item.get('sno', ''),
                    item.get('assigned_to', ''),
                    item.get('employee_name', ''),
                    item.get('inventory_id', ''),
                    item.get('project_id', ''),
                    item.get('product_id', ''),
                    item.get('inventory_name', ''),
                    item.get('description', ''),
                    item.get('quantity', ''),
                    item.get('status', ''),
                    self.parent.format_date(item.get('assigned_date', '')),
                    self.parent.format_date(item.get('submission_date', '')),
                    item.get('purpose_reason', ''),
                    item.get('assigned_by', ''),
                    item.get('comments', ''),
                    self.parent.format_date(item.get('assignment_return_date', '')),
                    item.get('assignment_barcode', ''),
                    item.get('zone_activity', ''),
                    item.get('location', ''),
                    item.get('client_name', '')
                ]
                self.parent.assigned_tree.insert('', 'end', values=values)
            
            # Auto-size columns after loading data
            self.auto_size_columns(self.parent.assigned_tree)
                
        except Exception as e:
            logger.error(f"Error refreshing assigned inventory list: {e}")
            messagebox.showerror("Error", "Could not refresh assigned inventory list")
    
    def auto_size_columns(self, tree):
        """Automatically resize columns to fit content"""
        default_font = font.nametofont("TkDefaultFont")
        
        for col in range(len(self.parent.headers)):
            # Get max width between header and content
            max_width = default_font.measure(self.parent.headers[col]) + 60
            
            # Check content width
            for item in tree.get_children():
                item_text = tree.set(item, col)
                item_width = default_font.measure(item_text)
                if item_width > max_width:
                    max_width = item_width + 60
            
            # Set column width with increased bounds (250-600 pixels) and no stretching
            tree.column(col, width=max(min(max_width, 750), 400), stretch=False)
