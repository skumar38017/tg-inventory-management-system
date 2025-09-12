# ~/frontend/app/homePage/search_results.py
from common_imports import *
from api_request.entry_inventory_api_request import search_inventory_by_id
from api_request.to_event_inventory_request import search_project_details_by_id
from reveal_qr_barcode_window import *

class SearchResults:
    def __init__(self, root):
        self.root = root
        self.search_results_listbox = None
        self.search_inventory_id_entry = None
        self.search_project_id_entry = None
        self.search_product_id_entry = None

    def create_search_results_tab(self, notebook):
        """Create the Search Results tab with all functionality"""
        # Frame 3: Search Results
        search_frame = tk.Frame(notebook, bg='white')
        notebook.add(search_frame, text="Search Results")

        # Search fields with modern styling
        search_fields_frame = tk.Frame(search_frame, bg='#ecf0f1', relief='raised', bd=1)
        search_fields_frame.pack(fill="x", pady=8, padx=8)
        
        for i in range(8):
            search_fields_frame.grid_columnconfigure(i, weight=1)

        # Row 1: First three search fields
        tk.Label(search_fields_frame, text="Inventory ID:", font=('Helvetica', 12, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=0, column=0, sticky='e', padx=5, pady=8)
        self.search_inventory_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 12), width=15,
                                           relief='flat', bd=5)
        self.search_inventory_id_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=8)

        tk.Label(search_fields_frame, text="Project ID:", font=('Helvetica', 12, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=0, column=2, sticky='e', padx=5, pady=8)
        self.search_project_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 12), width=15,
                                         relief='flat', bd=5)
        self.search_project_id_entry.grid(row=0, column=3, sticky='ew', padx=5, pady=8)

        tk.Label(search_fields_frame, text="Product ID:", font=('Helvetica', 12, 'bold'), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=0, column=4, sticky='e', padx=5, pady=8)
        self.search_product_id_entry = tk.Entry(search_fields_frame, font=('Helvetica', 12), width=15,
                                         relief='flat', bd=5)
        self.search_product_id_entry.grid(row=0, column=5, sticky='ew', padx=5, pady=8)

        # Search button with modern styling
        search_btn = tk.Button(search_fields_frame, text="Search", command=self.perform_search, 
                            font=('Helvetica', 12, 'bold'), height=1, width=12,
                            bg='#2c3e50', fg='white', relief='flat',
                            activebackground='#34495e', activeforeground='white')
        search_btn.grid(row=0, column=6, sticky='ew', padx=5, pady=8)

        # QR & Barcode button with modern styling
        reveal_btn = tk.Button(
            search_fields_frame,
            text="QR & Barcode", 
            font=('Helvetica', 12, 'bold'),
            width=15, height=1,
            bg='#95a5a6', fg='white', relief='flat',
            activebackground='#7f8c8d', activeforeground='white',
            command=self.open_reveal_window 
        )
        reveal_btn.grid(row=0, column=7, sticky='ew', padx=5, pady=8)
        search_fields_frame.grid_columnconfigure(7, weight=1)

        # Separator line
        ttk.Separator(search_frame, orient='horizontal').pack(fill="x", pady=5)

        # Search Results list container
        search_list_container = tk.Frame(search_frame)
        search_list_container.pack(fill="both", expand=True)

        # Calculate listbox height
        screen_height = self.root.winfo_screenheight()
        available_height = screen_height - 180
        list_frame_height = int(available_height * 0.8)
        listbox_height = max(8, list_frame_height // 35)

        # Create horizontal scrollbar first (placed at bottom)
        h_scrollbar = tk.Scrollbar(
            search_list_container,
            orient="horizontal",
            command=lambda *args: self.search_results_listbox.xview(*args)
        )
        h_scrollbar.pack(side="bottom", fill="x")

        # Then create vertical scrollbar (right side)
        v_scrollbar = tk.Scrollbar(
            search_list_container,
            orient="vertical",
            command=lambda *args: self.search_results_listbox.yview(*args)
        )
        v_scrollbar.pack(side="right", fill="y")

        # Create the listbox with both scrollbars
        self.search_results_listbox = tk.Listbox(
            search_list_container,
            height=listbox_height,
            font=('Courier New', 11),
            activestyle='none',
            selectbackground='#4a6984',
            selectforeground='white',
            bg='white',
            fg='black',
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        self.search_results_listbox.pack(side="left", fill="both", expand=True)
        
        # Setup modern scrolling for search results list
        setup_modern_scrolling(self.search_results_listbox)

    def perform_search(self):
        """Perform inventory search based on search criteria and display results in table format"""
        inventory_id = self.search_inventory_id_entry.get().strip()
        project_id = self.search_project_id_entry.get().strip()
        product_id = self.search_product_id_entry.get().strip()
        
        self.search_results_listbox.delete(0, tk.END)
        
        try:
            if project_id:
                # Project search remains the same but with empty string instead of N/A
                results = search_project_details_by_id(project_id)
                if not results:
                    messagebox.showinfo("Search Results", "No matching project found")
                    return
                    
                project = results[0]
                # Enhanced header with more project details
                header = (
                    f"Project: {project.get('project_name', '')} | "
                    f"Project_ID: {project.get('work_id', '')} | "
                    f"Employee: {project.get('employee_name', '')} | "
                    f"Client: {project.get('client_name', '')} | "
                    f"Location: {project.get('location', '')}\n"
                    f"Setup Date: {project.get('setup_date', '')} | "
                    f"Event Date: {project.get('event_date', '')}\n"
                    f"Submitted By: {project.get('submitted_by', '')} | "
                    f"Created At: {project.get('created_at', '')} | "
                    f"Updated At: {project.get('updated_at', '')}"
                    f"Barcode: {project.get('barcode', '')}\n"
                )
                self.search_results_listbox.insert(tk.END, header)
                self.search_results_listbox.insert(tk.END, "-"*125)
                self.search_results_listbox.insert(tk.END, "Inventory Items:")
                
                # Define inventory item headers
                item_headers = [
                    ("S.No", 30),
                    ("Name", 50),
                    ("Description", 50),
                    ("Qty", 16),
                    ("Zone", 35),
                    ("Material", 40),
                    ("Comments", 50),
                    ("Total", 16),
                    ("Unit", 16),
                    ("Per Unit Power", 25),
                    ("Total Power", 25),
                    ("Status", 25),
                    ("POC", 40),
                    ("Item ID", 40)
                ]
                
                # Create header row for inventory items
                header_row = "".join(f"{h[0]:<{h[1]}}" for h in item_headers)
                self.search_results_listbox.insert(tk.END, header_row)
                
                # Add separator line
                separator = "-" * sum(h[1] for h in item_headers)
                self.search_results_listbox.insert(tk.END, separator)
                
                # Display each inventory item with proper None handling
                for item in project.get('inventory_items', []):
                    # Safe getter function that handles None values
                    def safe_get(key, default=''):
                        val = item.get(key, default)
                        return str(val) if val is not None else default
                    
                    row_values = [
                        safe_get('sno')[:7],
                        safe_get('name')[:18],
                        safe_get('description')[:23],
                        safe_get('quantity')[:4],
                        safe_get('zone_active')[:12],
                        safe_get('material')[:13],
                        safe_get('comments')[:18],
                        safe_get('total')[:6],
                        safe_get('unit')[:6],
                        safe_get('per_unit_power')[:13],
                        safe_get('total_power')[:12],
                        safe_get('status')[:12],
                        safe_get('poc')[:13],
                        safe_get('id')[:36]
                    ]
                    
                    # Format the row
                    row = ""
                    for i, value in enumerate(row_values):
                        row += f"{value:<{item_headers[i][1]}}"
                    
                    self.search_results_listbox.insert(tk.END, row)
                    
                # Configure horizontal scrolling based on inventory items width
                self.search_results_listbox.config(width=sum(h[1] for h in item_headers))
                    
            elif inventory_id or product_id:
                # Handle inventory/product search with table format (existing code)
                results = search_inventory_by_id(
                    inventory_id=inventory_id,
                    product_id=product_id
                )
                
                if not results:
                    messagebox.showinfo("Search Results", "No matching items found")
                    return
                    
                # Define the column headers and their display widths
                headers = [
                    ("ID", 50),
                    ("Serial No.", 30),
                    ("InventoryID", 20),
                    ("Product ID", 20),
                    ("Name", 50),
                    ("Material", 40),
                    ("Total Quantity", 25),
                    ("Manufacturer", 40),
                    ("Purchase Dealer", 40),
                    ("Purchase Date", 35),
                    ("Purchase Amount", 25),
                    ("Repair Quantity", 25),
                    ("Repair Cost", 25),
                    ("On Rent", 30),
                    ("Vendor Name", 40),
                    ("Total Rent", 25),
                    ("Rented Inventory Returned", 30),
                    ("Returned Date", 30),
                    ("On Event", 25),
                    ("In Office", 30),
                    ("In Warehouse", 35),
                    ("Issued Qty", 25),
                    ("Balance Qty", 25),
                    ("Submitted By", 35),
                    ("Created At", 40),
                    ("Updated At", 40),
                    ("BarCode", 40),
                    ("BacodeUrl", 150)
                ]

                # Calculate total width needed
                total_width = sum(h[1] for h in headers)
                
                # Create header row
                header_row = "".join(f"{h[0]:<{h[1]}}" for h in headers)
                self.search_results_listbox.insert(tk.END, header_row)
                
                # Add separator line
                separator = "-" * total_width
                self.search_results_listbox.insert(tk.END, separator)
                
                # Add each item's values in a row
                for item in results:
                    row_values = []
                    for h in headers:
                        # Get the value using the exact header text (spaces included)
                        value = item.get(h[0], '')
                        
                        # Format the value to fit the column width
                        display_value = str(value)[:h[1]-2] + ".." if len(str(value)) > h[1] else str(value)
                        row_values.append(f"{display_value:<{h[1]}}")
                    
                    # Join all values with no extra spaces between columns
                    self.search_results_listbox.insert(tk.END, "".join(row_values))
                
                # Configure horizontal scrolling
                self.search_results_listbox.config(width=total_width)
                    
        except Exception as e:
            logger.error(f"Search failed: {str(e)}", exc_info=True)
            messagebox.showerror("Search Error", f"Failed to perform search: {str(e)}")

    def open_reveal_window(self):
        """Open the Reveal QR & Barcode window"""
        RevealQrAndBarcodeWindow(self.root).open_reveal_qr_and_barcode_pop_up()

    def clear_search_results(self):
        """Clear search results listbox"""
        if self.search_results_listbox:
            self.search_results_listbox.delete(0, tk.END)
