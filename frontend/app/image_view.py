from common_imports import *
from PIL import Image, ImageTk
import requests
from io import BytesIO
from api_request.entry_inventory_api_request import list_barcode_qrcode

class ImageViewWindow:
    root = None
    def __init__(self, root_window, selected_item=None):
        self.root = root_window
        self.qr_image = None
        self.barcode_image = None
        self.selected_item = selected_item  # Store the selected inventory item

    def open_image_view(self):
        """Open the Image View window with the specified layout"""
        if not self.root:
            raise ValueError("Root window not set for Image View")
        if not self.selected_item:
            messagebox.showerror("Error", "No inventory item selected")
            return
            
        # Create the window
        self.image_view_window = tk.Toplevel(self.root)
        self.image_view_window.title("QR & Barcode Image Views")
        self.image_view_window.geometry("800x600")
        self.image_view_window.resizable(False, False)
        
        # Main container with border
        main_frame = tk.Frame(self.image_view_window, bd=2, relief=tk.RAISED)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title label
        title_frame = tk.Frame(main_frame, bd=1, relief=tk.FLAT)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(title_frame, 
                             text="QR & Barcode Image Views", 
                             font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=5)
        
        # Horizontal separator
        separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=5, pady=5)
        
        # Images container frame
        images_frame = tk.Frame(main_frame)
        images_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # QR Code Section
        qr_frame = tk.LabelFrame(images_frame, text="QR CODE", bd=2, relief=tk.RAISED)
        qr_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # QR Image view with border
        qr_view_frame = tk.Frame(qr_frame, bd=1, relief=tk.SUNKEN)
        qr_view_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        self.qr_label = tk.Label(qr_view_frame, text="QR Code View", bg='white')
        self.qr_label.pack(fill=tk.BOTH, expand=True)
        
        # QR Buttons frame
        qr_btn_frame = tk.Frame(qr_frame)
        qr_btn_frame.pack(side=tk.BOTTOM, pady=10)
        
        tk.Button(qr_btn_frame, text="Print", width=10, command=self.print_qr).pack(side=tk.LEFT, padx=5)
        tk.Button(qr_btn_frame, text="Download", width=10, command=self.download_qr).pack(side=tk.LEFT, padx=5)
        tk.Button(qr_btn_frame, text="Share", width=10, command=self.share_qr).pack(side=tk.LEFT, padx=5)
        
        # Vertical separator
        separator = ttk.Separator(images_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=0)
        
        # Barcode Section
        barcode_frame = tk.LabelFrame(images_frame, text="BARCODE", bd=2, relief=tk.RAISED)
        barcode_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barcode Image view with border
        barcode_view_frame = tk.Frame(barcode_frame, bd=1, relief=tk.SUNKEN)
        barcode_view_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        self.barcode_label = tk.Label(barcode_view_frame, text="Barcode View", bg='white')
        self.barcode_label.pack(fill=tk.BOTH, expand=True)
        
        # Barcode Buttons frame
        barcode_btn_frame = tk.Frame(barcode_frame)
        barcode_btn_frame.pack(side=tk.BOTTOM, pady=10)
        
        tk.Button(barcode_btn_frame, text="Print", width=10, command=self.print_barcode).pack(side=tk.LEFT, padx=5)
        tk.Button(barcode_btn_frame, text="Download", width=10, command=self.download_barcode).pack(side=tk.LEFT, padx=5)
        tk.Button(barcode_btn_frame, text="Share", width=10, command=self.share_barcode).pack(side=tk.LEFT, padx=5)
        
        # Bottom separator
        separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=5, pady=5)
        
        # Close button frame
        close_frame = tk.Frame(main_frame)
        close_frame.pack(fill=tk.X, pady=5)
        
        # Close button
        close_button = tk.Button(close_frame, text="Close", width=15, 
                               command=self.image_view_window.destroy)
        close_button.pack(pady=5)
        
        # Fetch and display images
        self.fetch_images()

    def fetch_images(self):
        """Fetch QR and Barcode images from backend using the selected item's URLs"""
        try:
            # Get URLs from selected item
            qr_url = self.selected_item.get('QrCodeUrl')
            barcode_url = self.selected_item.get('BacodeUrl')
            
            if not qr_url or not barcode_url:
                raise ValueError("Missing image URLs in selected item")
            
            # Fetch QR code image
            qr_response = requests.get(qr_url)
            qr_response.raise_for_status()
            qr_image = Image.open(BytesIO(qr_response.content))
            qr_image = qr_image.resize((300, 300), Image.Resampling.LANCZOS)
            self.qr_image = ImageTk.PhotoImage(qr_image)
            self.qr_label.config(image=self.qr_image, text="")
            
            # Fetch Barcode image
            barcode_response = requests.get(barcode_url)
            barcode_response.raise_for_status()
            barcode_image = Image.open(BytesIO(barcode_response.content))
            barcode_image = barcode_image.resize((300, 100), Image.Resampling.LANCZOS)
            self.barcode_image = ImageTk.PhotoImage(barcode_image)
            self.barcode_label.config(image=self.barcode_image, text="")
            
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch images from server: {str(e)}")
            self.qr_label.config(text="Failed to load QR code")
            self.barcode_label.config(text="Failed to load barcode")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.qr_label.config(text="Error loading QR code")
            self.barcode_label.config(text="Error loading barcode")

    # Button action methods
    def print_qr(self):
        """Print QR code"""
        if self.qr_image:
            messagebox.showinfo("Print", "Printing QR code...")
            # Actual print implementation would go here
        else:
            messagebox.showerror("Error", "No QR code to print")

    def download_qr(self):
        """Download QR code"""
        if self.qr_image:
            messagebox.showinfo("Download", "Downloading QR code...")
            # Actual download implementation would go here
        else:
            messagebox.showerror("Error", "No QR code to download")

    def share_qr(self):
        """Share QR code"""
        if self.qr_image:
            messagebox.showinfo("Share", "Sharing QR code...")
            # Actual share implementation would go here
        else:
            messagebox.showerror("Error", "No QR code to share")

    def print_barcode(self):
        """Print Barcode"""
        if self.barcode_image:
            messagebox.showinfo("Print", "Printing barcode...")
            # Actual print implementation would go here
        else:
            messagebox.showerror("Error", "No barcode to print")

    def download_barcode(self):
        """Download Barcode"""
        if self.barcode_image:
            messagebox.showinfo("Download", "Downloading barcode...")
            # Actual download implementation would go here
        else:
            messagebox.showerror("Error", "No barcode to download")

    def share_barcode(self):
        """Share Barcode"""
        if self.barcode_image:
            messagebox.showinfo("Share", "Sharing barcode...")
            # Actual share implementation would go here
        else:
            messagebox.showerror("Error", "No barcode to share")