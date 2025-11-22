# frontend/app/reveal_qr_&_barcode_window.py
from common_imports import *
from image_view import *
from api_request.entry_inventory_api_request import list_barcode_qrcode
from utils.universal_font_box_size import universal_font_box_size
from utils.window_utils import setup_modern_scrolling, custom_messagebox

class RevealQrAndBarcodeWindow:
    root = None
    def __init__(self, root_window):
        self.root = root_window
        self.selected_item = None
        self.selection_var = tk.IntVar(value=0)
        self.row_buttons = []

    def open_reveal_qr_and_barcode_pop_up(self):
        """Open the modern QR & Barcode window"""
        if not self.root:
            raise ValueError("Root window not set for RevealQrAndBarcodeWindow")
            
        # Create modern window
        self.reveal_qr_and_barcode_window = tk.Toplevel(self.root)
        self.reveal_qr_and_barcode_window.title(universal_font_box_size.qr_barcode_window_title)
        self.reveal_qr_and_barcode_window.geometry(universal_font_box_size.qr_barcode_window_geometry)
        self.reveal_qr_and_barcode_window.configure(bg='#f0f0f0')
        
        # Modern styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TFrame', background='#ffffff', relief='flat')
        style.configure('Header.TLabel', background='#2c3e50', foreground='white', 
                       font=(universal_font_box_size.qr_barcode_header_font_family, 
                            universal_font_box_size.qr_barcode_header_font_size, 
                            universal_font_box_size.qr_barcode_header_font_weight))
        style.configure('Modern.TButton', 
                       font=(universal_font_box_size.qr_barcode_button_font_family, 
                            universal_font_box_size.qr_barcode_button_font_size), 
                       padding=10)
        style.configure('Treeview', font=('Helvetica', universal_font_box_size.qr_barcode_header_font_size))
        style.configure('Treeview.Heading', font=('Helvetica', universal_font_box_size.qr_barcode_header_font_size, 'bold'))
        
        # Header frame
        header_frame = ttk.Frame(self.reveal_qr_and_barcode_window, style='Modern.TFrame')
        header_frame.pack(fill='x', padx=universal_font_box_size.qr_barcode_main_frame_padx, 
                         pady=(universal_font_box_size.qr_barcode_main_frame_pady, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="QR & Barcode Manager", 
                               font=(universal_font_box_size.qr_barcode_title_font_family, 
                                    universal_font_box_size.qr_barcode_title_font_size, 
                                    universal_font_box_size.qr_barcode_title_font_weight), 
                               foreground='#2c3e50', background='#ffffff')
        title_label.pack(side='left')
        
        # Search frame
        search_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        search_frame.pack(side='right')
        
        ttk.Label(search_frame, text="Search:", 
                 font=(universal_font_box_size.search_label_font_family, 
                      universal_font_box_size.search_label_font_size), 
                 background='#ffffff').pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                               font=(universal_font_box_size.search_entry_font_family, 
                                    universal_font_box_size.search_entry_font_size), 
                               width=universal_font_box_size.search_entry_width)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_data)
        
        # Main content frame
        content_frame = ttk.Frame(self.reveal_qr_and_barcode_window, style='Modern.TFrame')
        content_frame.pack(fill='both', expand=True, 
                          padx=universal_font_box_size.qr_barcode_main_frame_padx, 
                          pady=10)
        
        # Create modern table
        self.create_modern_table(content_frame)
        
        # Button frame with modern styling
        button_frame = ttk.Frame(self.reveal_qr_and_barcode_window, style='Modern.TFrame')
        button_frame.pack(fill='x', padx=universal_font_box_size.qr_barcode_main_frame_padx, 
                         pady=(universal_font_box_size.qr_barcode_button_frame_pady, 
                              universal_font_box_size.qr_barcode_main_frame_pady))
        
        # Modern buttons
        ttk.Button(button_frame, text="Load Data", style='Modern.TButton',
                  command=self.load_data).pack(side='left', 
                                              padx=(0, universal_font_box_size.qr_barcode_button_padx))
        
        self.image_view_button = ttk.Button(button_frame, text="View Images", 
                                          style='Modern.TButton', command=self.open_image_view, 
                                          state='disabled')
        self.image_view_button.pack(side='left', padx=(0, universal_font_box_size.qr_barcode_button_padx))
        
        ttk.Button(button_frame, text="Close", style='Modern.TButton',
                  command=self.reveal_qr_and_barcode_window.destroy).pack(side='right')
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.reveal_qr_and_barcode_window, textvariable=self.status_var, 
                              font=(universal_font_box_size.search_label_font_family, 9), 
                              background='#ecf0f1', foreground='#7f8c8d')
        status_bar.pack(fill='x', side='bottom')
        
        self.reveal_qr_and_barcode_window.resizable(True, True)

    def create_modern_table(self, parent):
        """Create modern table with Treeview"""
        # Table frame
        table_frame = ttk.Frame(parent, style='Modern.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        # Create Treeview with modern styling
        columns = ('Select', 'Serial', 'Inventory ID', 'Name', 'Barcode URL', 'QR Code URL')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure column headings
        self.tree.heading('Select', text='Select')
        self.tree.heading('Serial', text='Serial No.')
        self.tree.heading('Inventory ID', text='Inventory ID')
        self.tree.heading('Name', text='Item Name')
        self.tree.heading('Barcode URL', text='Barcode URL')
        self.tree.heading('QR Code URL', text='QR Code URL')
        
        # Configure column widths - full size for horizontal scrolling
        self.tree.column('Select', width=100, anchor='w', stretch=True)
        self.tree.column('Serial', width=universal_font_box_size.S_No * 10, anchor='w', stretch=True)
        self.tree.column('Inventory ID', width=universal_font_box_size.InventoryID * 10, anchor='w', stretch=True)
        self.tree.column('Name', width=universal_font_box_size.Name * 10, anchor='w', stretch=True)
        self.tree.column('Barcode URL', width=universal_font_box_size.BarcodeUrl * 10, anchor='w', stretch=True)
        self.tree.column('QR Code URL', width=universal_font_box_size.BarcodeUrl * 10, anchor='w', stretch=True)
        
        # Modern scrollbars - proper positioning
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Apply modern scrolling like Added Items List
        setup_modern_scrolling(self.tree)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Bind arrow key scrolling
        self.tree.bind('<Left>', self.scroll_left)
        self.tree.bind('<Right>', self.scroll_right)
        self.tree.bind('<Up>', self.scroll_up)
        self.tree.bind('<Down>', self.scroll_down)
        self.tree.focus_set()  # Enable keyboard focus
        
        # Modern row styling
        self.tree.tag_configure('evenrow', background='#f8f9fa')
        self.tree.tag_configure('oddrow', background='#ffffff')
        self.tree.tag_configure('selected', background='#3498db', foreground='white')

    def load_data(self):
        """Load data with modern progress indication"""
        self.status_var.set("Loading data...")
        self.reveal_qr_and_barcode_window.update()
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.selected_item = None
        self.image_view_button.config(state='disabled')
        
        try:
            # Fetch data from backend
            backend_data = list_barcode_qrcode()
            self.all_data = backend_data  # Store for filtering
            
            # Populate table
            self.populate_table(backend_data)
            
            self.status_var.set(f"Loaded {len(backend_data)} items")
            
        except Exception as e:
            custom_messagebox("error", "Error", f"Failed to load data: {str(e)}")
            self.status_var.set("Error loading data")

    def populate_table(self, data):
        """Populate table with data"""
        for i, item in enumerate(data):
            # Determine row tag for alternating colors
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Insert data
            self.tree.insert('', 'end', values=(
                'O',  # Select indicator
                str(i + 1),  # Serial number
                item.get("InventoryID", ""),
                item.get("Name", ""),
                item.get("BacodeUrl", ""),
                item.get("QrCodeUrl", "")
            ), tags=(tag,))

    def filter_data(self, event=None):
        """Filter data based on search input"""
        if not hasattr(self, 'all_data'):
            return
            
        search_term = self.search_var.get().lower()
        
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter data
        if search_term:
            filtered_data = [
                item for item in self.all_data
                if search_term in item.get("InventoryID", "").lower() or
                   search_term in item.get("Name", "").lower()
            ]
        else:
            filtered_data = self.all_data
        
        # Repopulate table
        self.populate_table(filtered_data)
        self.status_var.set(f"Showing {len(filtered_data)} of {len(self.all_data)} items")

    def on_item_select(self, event):
        """Handle item selection in treeview"""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            values = self.tree.item(item_id, 'values')
            
            # Find the corresponding data item
            serial_no = int(values[1]) - 1
            if hasattr(self, 'all_data') and 0 <= serial_no < len(self.all_data):
                self.selected_item = self.all_data[serial_no]
                self.image_view_button.config(state='normal')
                
                # Highlight selected row
                for item in self.tree.get_children():
                    self.tree.set(item, 'Select', 'O')
                self.tree.set(item_id, 'Select', 'X')

    def open_image_view(self):
        """Open the Image View window for the selected item"""
        if not self.selected_item:
            custom_messagebox("error", "Error", "Please select an item first")
            return
            
        try:
            image_viewer = ImageViewWindow(self.root, self.selected_item)
            image_viewer.open_image_view()
        except Exception as e:
            custom_messagebox("error", "Error", f"Failed to open image view: {str(e)}")

    def scroll_left(self, event):
        """Scroll table left with arrow key"""
        self.tree.xview_scroll(-10, "units")
        return "break"
    
    def scroll_right(self, event):
        """Scroll table right with arrow key"""
        self.tree.xview_scroll(10, "units")
        return "break"
    
    def scroll_up(self, event):
        """Scroll table up with arrow key"""
        self.tree.yview_scroll(-10, "units")
        return "break"
    
    def scroll_down(self, event):
        """Scroll table down with arrow key"""
        self.tree.yview_scroll(10, "units")
        return "break"

    # Legacy methods for compatibility
    def create_table_structure(self):
        """Legacy method - redirects to modern table"""
        pass

    def _sync_horizontal_scroll(self, *args):
        """Legacy method - no longer needed with Treeview"""
        pass
        
    def _configure_header(self, event):
        """Legacy method - no longer needed with Treeview"""
        pass
        
    def _configure_data(self, event):
        """Legacy method - no longer needed with Treeview"""
        pass

    def select_item(self, row, item):
        """Legacy method for compatibility"""
        self.selected_item = item
        self.image_view_button.config(state='normal')
        
    def fetch_data_from_backend(self):
        """Fetch data using list_barcode_qrcode function"""
        return list_barcode_qrcode()