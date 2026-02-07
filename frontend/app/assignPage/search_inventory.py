# frontend/app/assignPage/search_inventory.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.assign_inventory_api_request import search_assigned_inventory_by_id

class SearchInventorySection:
    def __init__(self, parent_window, parent_instance):
        self.window = parent_window
        self.parent = parent_instance
        
    def create_search_section(self):
        """Create the search fields section"""
        #  ----------------------- Search Buttons Header Section -----------------------
        # Search fields in row 3
        search_frame = tk.Frame(self.window)
        search_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        tk.Label(search_frame, text="Inventory ID:", font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold')).grid(row=0, column=0, sticky='e', padx=5)
        self.parent.inventory_id = tk.Entry(search_frame, font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), width=universal_font_box_size.search_entry_width, justify='center')
        self.parent.inventory_id.grid(row=0, column=1, sticky='w', padx=5)
        
        tk.Label(search_frame, text="Project ID:", font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold')).grid(row=0, column=2, sticky='e', padx=5)
        self.parent.project_id = tk.Entry(search_frame, font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), width=universal_font_box_size.search_entry_width, justify='center')
        self.parent.project_id.grid(row=0, column=3, sticky='w', padx=5)
        
        tk.Label(search_frame, text="Product ID:", font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold')).grid(row=0, column=4, sticky='e', padx=5)
        self.parent.product_id = tk.Entry(search_frame, font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), width=universal_font_box_size.search_entry_width, justify='center')
        self.parent.product_id.grid(row=0, column=5, sticky='w', padx=5)
        
        tk.Label(search_frame, text="Employee Name:", font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold')).grid(row=0, column=6, sticky='e', padx=5)
        self.parent.employee_name = tk.Entry(search_frame, font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), width=universal_font_box_size.search_entry_width, justify='center')
        self.parent.employee_name.grid(row=0, column=7, sticky='w', padx=5)
        
        #  ----------------------- End of Search Buttons Header Section -----------------------
        
        return search_frame
    
    def search_product(self):
        """Handle product search with proper error handling"""
        try:
            inventory_id = self.parent.inventory_id.get().strip()
            project_id = self.parent.project_id.get().strip()
            product_id = self.parent.product_id.get().strip()
            employee_name = self.parent.employee_name.get().strip()
            
            if not any([inventory_id, project_id, product_id, employee_name]):
                messagebox.showwarning("Warning", "Please enter at least one search criteria")
                return

            results = search_assigned_inventory_by_id(
                inventory_id=inventory_id,
                project_id=project_id,
                product_id=product_id,
                employee_name=employee_name
            )
            
            if results:
                # Clear existing items
                self.parent.assigned_tree.delete(*self.parent.assigned_tree.get_children())
                
                # Add search results
                for item in results:
                    self.parent.assigned_tree.insert('', 'end', values=[
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
                    ])
            else:
                messagebox.showinfo("Info", "No matching records found")
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            messagebox.showerror("Error", str(e))
