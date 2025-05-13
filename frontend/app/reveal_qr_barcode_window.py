# frontend/app/reveal_qr_&_barcode_window.py
from common_imports import *

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
        
        # Create the table structure
        self.create_table_structure()
        
        # Button frame
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=(10, 0))
        
        # Close button
        close_button = tk.Button(button_frame, text="Close", 
                               command=self.reveal_qr_and_barcode_window.destroy)
        close_button.pack(side='left', padx=5)
        
        # Refresh button
        refresh_button = tk.Button(button_frame, text="Refresh", 
                                 command=self.refresh_data)
        refresh_button.pack(side='left', padx=5)
        
        # Load initial data
        self.refresh_data()
        
        # Make the window resizable
        self.reveal_qr_and_barcode_window.resizable(True, True)

    def create_table_structure(self):
        """Create the table structure (headers and grid configuration)"""
        # Create a frame for the table
        self.table_frame = tk.Frame(self.main_frame, borderwidth=1, relief="solid")
        self.table_frame.pack(fill='both', expand=True)
        
        # Create header row
        headers = ["Serial No.", "Inventory Name", "Barcode URL", "QR Code URL"]
        for col, header in enumerate(headers):
            header_label = tk.Label(self.table_frame, text=header, borderwidth=1, relief="solid", 
                                  padx=5, pady=5, font=('Helvetica', 12, 'bold'))
            header_label.grid(row=0, column=col, sticky="nsew")
            self.table_frame.grid_columnconfigure(col, weight=1)
        
        # Configure all columns to expand equally
        for i in range(4):
            self.table_frame.grid_columnconfigure(i, weight=1)

    def refresh_data(self):
        """Fetch data from backend and populate the table"""
        # First clear any existing data rows (except headers)
        for widget in self.table_frame.winfo_children():
            if widget.grid_info()["row"] > 0:  # Skip header row
                widget.destroy()
        
        # Fetch data from backend (replace this with your actual backend call)
        backend_data = self.fetch_data_from_backend()
        
        # Add data rows
        for row, item in enumerate(backend_data, start=1):
            # Serial number (auto-increment)
            serial_label = tk.Label(self.table_frame, text=str(row), borderwidth=1, 
                                  relief="solid", padx=5, pady=5)
            serial_label.grid(row=row, column=0, sticky="nsew")
            
            # Inventory Name (from backend)
            name_label = tk.Label(self.table_frame, text=item["name"], borderwidth=1, 
                                 relief="solid", padx=5, pady=5)
            name_label.grid(row=row, column=1, sticky="nsew")
            
            # Barcode URL (from backend)
            barcode_label = tk.Label(self.table_frame, text=item["barcode_url"], 
                                    borderwidth=1, relief="solid", padx=5, pady=5)
            barcode_label.grid(row=row, column=2, sticky="nsew")
            
            # QR Code URL (from backend)
            qrcode_label = tk.Label(self.table_frame, text=item["qrcode_url"], 
                                  borderwidth=1, relief="solid", padx=5, pady=5)
            qrcode_label.grid(row=row, column=3, sticky="nsew")
            
            # Configure row to expand
            self.table_frame.grid_rowconfigure(row, weight=1)

    def fetch_data_from_backend(self):
        """Replace this method with actual backend data fetching logic"""
        # This is a placeholder - implement your actual backend connection here
        # Should return a list of dictionaries with keys: name, barcode_url, qrcode_url
        raise NotImplementedError("Implement this method to fetch data from your backend")