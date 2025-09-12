# ~/frontend/app/homePage/search_results.py
from common_imports import *
from api_request.entry_inventory_api_request import search_inventory_by_id
from api_request.to_event_inventory_request import search_project_details_by_id
from homePage.reveal_qr_barcode_window import *
from utils.universal_font_box_size import universal_font_box_size

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
        search_frame = tk.Frame(notebook, bg=universal_font_box_size.search_frame_bg)
        notebook.add(search_frame, text="Search Results")

        # Search fields with modern styling
        search_fields_frame = tk.Frame(search_frame, 
                                     bg=universal_font_box_size.search_fields_frame_bg, 
                                     relief=universal_font_box_size.search_fields_frame_relief, 
                                     bd=universal_font_box_size.search_fields_frame_bd)
        search_fields_frame.pack(fill="x", 
                               pady=universal_font_box_size.search_frame_pady, 
                               padx=universal_font_box_size.search_frame_padx)
        
        for i in range(8):
            search_fields_frame.grid_columnconfigure(i, weight=1)

        # Row 1: First three search fields
        tk.Label(search_fields_frame, text="Inventory ID:", 
                font=(universal_font_box_size.search_label_font_family, universal_font_box_size.search_label_font_size, universal_font_box_size.search_label_font_weight), 
                bg=universal_font_box_size.search_fields_frame_bg, 
                fg=universal_font_box_size.search_label_fg).grid(row=0, column=0, sticky='e', 
                                                                padx=universal_font_box_size.search_grid_padx, 
                                                                pady=universal_font_box_size.search_grid_pady)
        self.search_inventory_id_entry = tk.Entry(search_fields_frame, 
                                           font=(universal_font_box_size.search_entry_font_family, universal_font_box_size.search_entry_font_size), 
                                           width=universal_font_box_size.search_entry_width,
                                           relief=universal_font_box_size.search_entry_relief, 
                                           bd=universal_font_box_size.search_entry_bd)
        self.search_inventory_id_entry.grid(row=0, column=1, sticky='ew', 
                                          padx=universal_font_box_size.search_grid_padx, 
                                          pady=universal_font_box_size.search_grid_pady)

        tk.Label(search_fields_frame, text="Project ID:", 
                font=(universal_font_box_size.search_label_font_family, universal_font_box_size.search_label_font_size, universal_font_box_size.search_label_font_weight), 
                bg=universal_font_box_size.search_fields_frame_bg, 
                fg=universal_font_box_size.search_label_fg).grid(row=0, column=2, sticky='e', 
                                                                padx=universal_font_box_size.search_grid_padx, 
                                                                pady=universal_font_box_size.search_grid_pady)
        self.search_project_id_entry = tk.Entry(search_fields_frame, 
                                         font=(universal_font_box_size.search_entry_font_family, universal_font_box_size.search_entry_font_size), 
                                         width=universal_font_box_size.search_entry_width,
                                         relief=universal_font_box_size.search_entry_relief, 
                                         bd=universal_font_box_size.search_entry_bd)
        self.search_project_id_entry.grid(row=0, column=3, sticky='ew', 
                                         padx=universal_font_box_size.search_grid_padx, 
                                         pady=universal_font_box_size.search_grid_pady)

        tk.Label(search_fields_frame, text="Product ID:", 
                font=(universal_font_box_size.search_label_font_family, universal_font_box_size.search_label_font_size, universal_font_box_size.search_label_font_weight), 
                bg=universal_font_box_size.search_fields_frame_bg, 
                fg=universal_font_box_size.search_label_fg).grid(row=0, column=4, sticky='e', 
                                                                padx=universal_font_box_size.search_grid_padx, 
                                                                pady=universal_font_box_size.search_grid_pady)
        self.search_product_id_entry = tk.Entry(search_fields_frame, 
                                         font=(universal_font_box_size.search_entry_font_family, universal_font_box_size.search_entry_font_size), 
                                         width=universal_font_box_size.search_entry_width,
                                         relief=universal_font_box_size.search_entry_relief, 
                                         bd=universal_font_box_size.search_entry_bd)
        self.search_product_id_entry.grid(row=0, column=5, sticky='ew', 
                                         padx=universal_font_box_size.search_grid_padx, 
                                         pady=universal_font_box_size.search_grid_pady)

        # Search button with modern styling
        search_btn = tk.Button(search_fields_frame, text="Search", command=self.perform_search, 
                            font=(universal_font_box_size.search_button_font_family, universal_font_box_size.search_button_font_size, universal_font_box_size.search_button_font_weight), 
                            height=universal_font_box_size.search_button_height, 
                            width=universal_font_box_size.search_button_width,
                            bg='#2c3e50', fg='white', relief=universal_font_box_size.search_button_relief,
                            activebackground='#34495e', activeforeground='white')
        search_btn.grid(row=0, column=6, sticky='ew', 
                       padx=universal_font_box_size.search_grid_padx, 
                       pady=universal_font_box_size.search_grid_pady)

        # QR & Barcode button with modern styling
        reveal_btn = tk.Button(
            search_fields_frame,
            text="QR & Barcode", 
            font=(universal_font_box_size.search_button_font_family, universal_font_box_size.search_button_font_size, universal_font_box_size.search_button_font_weight),
            width=universal_font_box_size.qr_barcode_button_width, 
            height=universal_font_box_size.qr_barcode_button_height,
            bg='#95a5a6', fg='white', relief=universal_font_box_size.search_button_relief,
            activebackground='#7f8c8d', activeforeground='white',
            command=self.open_reveal_window 
        )
        reveal_btn.grid(row=0, column=7, sticky='ew', 
                       padx=universal_font_box_size.search_grid_padx, 
                       pady=universal_font_box_size.search_grid_pady)
        search_fields_frame.grid_columnconfigure(7, weight=1)

        # Separator line
        ttk.Separator(search_frame, orient='horizontal').pack(fill="x", pady=universal_font_box_size.search_separator_pady)

        # Search Results list container
        search_list_container = tk.Frame(search_frame)
        search_list_container.pack(fill="both", expand=True)

        # Calculate listbox height
        screen_height = self.root.winfo_screenheight()
        available_height = screen_height - universal_font_box_size.search_screen_height_offset
        list_frame_height = int(available_height * universal_font_box_size.search_height_multiplier)
        listbox_height = max(universal_font_box_size.search_min_listbox_height, list_frame_height // universal_font_box_size.search_height_divisor)

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
            font=(universal_font_box_size.search_results_font_family, universal_font_box_size.search_results_font_size),
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
                self.search_results_listbox.insert(tk.END, "-"*universal_font_box_size.search_separator_length)
                self.search_results_listbox.insert(tk.END, "Inventory Items:")
                
                # Use centralized inventory item headers
                item_headers = universal_font_box_size.inventory_item_headers
                
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
                    
                # Use centralized column headers
                headers = universal_font_box_size.inventory_column_headers

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
