# frontend/app/reveal_qr_&_barcode_window.py
from common_imports import *
from api_request.entry_inventory_api_request import list_barcode_qrcode

class RevealQrAndBarcodeWindow:
    root = None
    def __init__(self, root_window):
        self.root = root_window

    def open_reveal_qr_and_barcode_pop_up(self):
        """Open the Reveal QR & Barcode pop-up window"""
        if not self.root:
            raise ValueError("Root window not set for RevealQrAndBarcodeWindow")
            
        # Create the window
        self.reveal_qr_and_barcode_window = tk.Toplevel(self.root)
        self.reveal_qr_and_barcode_window.title("Reveal QR & Barcode")
        self.reveal_qr_and_barcode_window.geometry("1000x800")
        
        # Main container
        self.main_frame = tk.Frame(self.reveal_qr_and_barcode_window)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title label
        title_label = tk.Label(self.main_frame, text="QR & Barcode", font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create the table structure with scrollbars
        self.create_table_structure()
        
        # Button frame
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=(10, 0))
        
        # Close button
        close_button = tk.Button(button_frame, text="Close", 
                               command=self.reveal_qr_and_barcode_window.destroy)
        close_button.pack(side='left', padx=5)
        
        # Load button
        load_button = tk.Button(button_frame, text="Load", 
                              command=self.load_data)
        load_button.pack(side='left', padx=5)
                
        # Make the window resizable
        self.reveal_qr_and_barcode_window.resizable(True, True)

    def create_table_structure(self):
        """Create the table structure with both vertical and horizontal scrollbars"""
        # Create a container frame for the table and scrollbars
        table_container = tk.Frame(self.main_frame)
        table_container.pack(fill='both', expand=True)
        
        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(table_container, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        # Create horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(table_container, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Create a canvas for the table with scrollbars
        self.table_canvas = tk.Canvas(table_container, 
                                    yscrollcommand=v_scrollbar.set,
                                    xscrollcommand=h_scrollbar.set)
        self.table_canvas.pack(side='left', fill='both', expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.table_canvas.yview)
        h_scrollbar.config(command=self.table_canvas.xview)
        
        # Create the table frame inside the canvas
        self.table_frame = tk.Frame(self.table_canvas)
        self.table_canvas.create_window((0, 0), window=self.table_frame, anchor='nw')
        
        # Bind the canvas to configure the scroll region when the table size changes
        self.table_frame.bind('<Configure>', lambda e: self.table_canvas.configure(
            scrollregion=self.table_canvas.bbox('all')))
        
        # Bind mousewheel to scroll vertically
        self.table_canvas.bind_all("<MouseWheel>", lambda e: self.table_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Bind shift+mousewheel to scroll horizontally
        self.table_canvas.bind_all("<Shift-MouseWheel>", lambda e: self.table_canvas.xview_scroll(int(-1*(e.delta/120))), "units")
        
        # Create header row
        headers = ["Serial No.", "Inventory ID", "Inventory Name", "Barcode URL", "QR Code URL"]
        for col, header in enumerate(headers):
            header_label = tk.Label(self.table_frame, text=header, borderwidth=1, relief="solid", 
                                  padx=5, pady=5, font=('Helvetica', 12, 'bold'))
            header_label.grid(row=0, column=col, sticky="nsew")
            self.table_frame.grid_columnconfigure(col, weight=1)
        
        # Configure all columns to expand equally
        for i in range(len(headers)):
            self.table_frame.grid_columnconfigure(i, weight=1)

    def load_data(self):
        """Load data using list_barcode_qrcode function"""
        # Clear existing data first
        for widget in self.table_frame.winfo_children():
            if widget.grid_info()["row"] > 0:  # Skip header row
                widget.destroy()
        
        # Fetch data from backend using list_barcode_qrcode
        backend_data = list_barcode_qrcode()
        
        # Add data rows
        for row, item in enumerate(backend_data, start=1):
            # Serial number (auto-increment)
            serial_label = tk.Label(self.table_frame, text=str(row), borderwidth=1, 
                                  relief="solid", padx=5, pady=5)
            serial_label.grid(row=row, column=0, sticky="nsew")

            # Inventory ID (from backend)
            inventory_id_label = tk.Label(self.table_frame, text=item["InventoryID"], borderwidth=1, 
                                 relief="solid", padx=5, pady=5)
            inventory_id_label.grid(row=row, column=1, sticky="nsew")
            
            # Inventory Name (from backend)
            name_label = tk.Label(self.table_frame, text=item["Name"], borderwidth=1, 
                                 relief="solid", padx=5, pady=5)
            name_label.grid(row=row, column=2, sticky="nsew")
            
            # Barcode URL (from backend)
            barcode_label = tk.Label(self.table_frame, text=item["BacodeUrl"], 
                                    borderwidth=1, relief="solid", padx=5, pady=5)
            barcode_label.grid(row=row, column=3, sticky="nsew")
            
            # QR Code URL (from backend)
            qrcode_label = tk.Label(self.table_frame, text=item["QrCodeUrl"], 
                                  borderwidth=1, relief="solid", padx=5, pady=5)
            qrcode_label.grid(row=row, column=4, sticky="nsew")
            
            # Configure row to expand
            self.table_frame.grid_rowconfigure(row, weight=1)
        
        # Update the scroll region after adding data
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox('all'))

    def fetch_data_from_backend(self):
        """Fetch data using list_barcode_qrcode function"""
        return list_barcode_qrcode()