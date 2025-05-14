from common_imports import *
from PIL import Image, ImageTk
import requests
from io import BytesIO
import base64
import tempfile
import webbrowser
from tkinter import filedialog
from api_request.entry_inventory_api_request import list_barcode_qrcode

class ImageViewWindow:
    root = None
    def __init__(self, root_window, selected_item=None):
        self.root = root_window
        self.qr_image = None
        self.barcode_image = None
        self.selected_item = selected_item  # Store the selected inventory item
        self.name = selected_item.get('Name', 'item') if selected_item else 'item'

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
            
            # Fetch QR code image and store original
            qr_response = requests.get(qr_url)
            qr_response.raise_for_status()
            self.original_qr_image = Image.open(BytesIO(qr_response.content))  # Store original
            qr_image = self.original_qr_image.resize((300, 300), Image.Resampling.LANCZOS)
            self.qr_image = ImageTk.PhotoImage(qr_image)
            self.qr_label.config(image=self.qr_image, text="")
            
            # Fetch Barcode image and store original
            barcode_response = requests.get(barcode_url)
            barcode_response.raise_for_status()
            self.original_barcode_image = Image.open(BytesIO(barcode_response.content))  # Store original
            barcode_image = self.original_barcode_image.resize((300, 100), Image.Resampling.LANCZOS)
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

    def download_image(self, image_type):
        """Generic download method for both QR and barcode - ensures local machine download"""
        try:
            # Determine image-specific parameters
            if image_type == 'qr':
                if not hasattr(self, 'original_qr_image'):
                    raise ValueError("No QR code to download")
                img = self.original_qr_image  # Use stored original image
                suffix = 'qrcode'
            else:
                if not hasattr(self, 'original_barcode_image'):
                    raise ValueError("No barcode to download")
                img = self.original_barcode_image  # Use stored original image
                suffix = 'brcode'

            # Create filename with requested format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name}_{timestamp}_{suffix}.png"
            
            # Use a file dialog to ensure local machine download
            filepath = filedialog.asksaveasfilename(
                initialdir=os.path.expanduser('~'),
                initialfile=filename,
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if not filepath:  # User cancelled the dialog
                return
                
            # Save the image to the selected location
            img.save(filepath, 'PNG')
            messagebox.showinfo("Success", f"Image saved to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download image: {str(e)}")

    def download_qr(self):
        """Download QR code to default downloads folder"""
        self.download_image('qr')

    def download_barcode(self):
        """Download Barcode to default downloads folder"""
        self.download_image('barcode')

    def get_available_printers(self):
        """Get list of available printers on the system"""
        try:
            if os.name == 'nt':  # Windows
                import win32print
                printers = [printer[2] for printer in win32print.EnumPrinters(2)]
            elif sys.platform == 'darwin':  # macOS
                import subprocess
                output = subprocess.check_output(['lpstat', '-a']).decode('utf-8')
                printers = [line.split()[0] for line in output.split('\n') if line]
            else:  # Linux
                import subprocess
                output = subprocess.check_output(['lpstat', '-a']).decode('utf-8')
                printers = [line.split()[0] for line in output.split('\n') if line]
            return printers
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get printer list: {str(e)}")
            return []

    def print_image(self, image_type):
        """Generic print method with printer selection"""
        try:
            # Get available printers
            printers = self.get_available_printers()
            if not printers:
                messagebox.showerror("Error", "No printers available")
                return

            # Create printer selection dialog
            printer_window = tk.Toplevel(self.root)
            printer_window.title("Select Printer")
            printer_window.geometry("400x300")
            
            tk.Label(printer_window, 
                    text="Select a printer:",
                    font=('Helvetica', 12)).pack(pady=10)
            
            # Printer listbox
            printer_list = tk.Listbox(printer_window)
            for printer in printers:
                printer_list.insert(tk.END, printer)
            printer_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Print button
            print_button = tk.Button(printer_window, text="Print",
                                command=lambda: self.execute_print(
                                    image_type, 
                                    printer_list.get(tk.ACTIVE),
                                    printer_window))
            print_button.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize printing: {str(e)}")

    def execute_print(self, image_type, printer_name, window=None):
        """Execute the actual printing to selected printer"""
        try:
            if not printer_name:
                messagebox.showerror("Error", "No printer selected")
                return
                
            # Determine which image to print
            if image_type == 'qr':
                if not hasattr(self, 'original_qr_image'):
                    raise ValueError("No QR code to print")
                img = self.original_qr_image.copy()
                standard_size = (2, 2)  # 2x2 inches for QR
            else:
                if not hasattr(self, 'original_barcode_image'):
                    raise ValueError("No barcode to print")
                img = self.original_barcode_image.copy()
                standard_size = (3, 1)  # 3x1 inches for barcode

            # Convert inches to pixels (300 DPI)
            dpi = 300
            size_in_pixels = (int(standard_size[0] * dpi), (int(standard_size[1] * dpi)))
            
            # Resize image while maintaining aspect ratio
            img.thumbnail(size_in_pixels, Image.Resampling.LANCZOS)
            
            # Create white background
            background = Image.new('RGB', size_in_pixels, (255, 255, 255))
            x = (size_in_pixels[0] - img.size[0]) // 2
            y = (size_in_pixels[1] - img.size[1]) // 2
            background.paste(img, (x, y))

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_path = tmp.name
                background.save(temp_path, 'PNG')

            # Platform-specific printing
            if os.name == 'nt':  # Windows
                import win32print
                import win32api
                win32api.ShellExecute(0, "print", temp_path, f'/d:"{printer_name}"', ".", 0)
            elif sys.platform == 'darwin':  # macOS
                import subprocess
                subprocess.run(['lpr', '-P', printer_name, temp_path])
            else:  # Linux
                import subprocess
                subprocess.run(['lp', '-d', printer_name, temp_path])
                
            messagebox.showinfo("Print", f"Print job sent to {printer_name}")
            
            # Clean up temp file after delay
            self.root.after(10000, lambda: os.unlink(temp_path) if os.path.exists(temp_path) else None)
            
            if window:
                window.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {str(e)}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)

    def print_qr(self):
        """Print QR code with printer selection"""
        self.print_image('qr')

    def print_barcode(self):
        """Print Barcode with printer selection"""
        self.print_image('barcode')

    def generate_share_link(self, image_type):
        """Generate a shareable link for the image"""
        try:
            # Determine which image to share
            if image_type == 'qr':
                if not hasattr(self, 'original_qr_image'):
                    raise ValueError("No QR code to share")
                img = self.original_qr_image
                suffix = 'qrcode'
            else:
                if not hasattr(self, 'original_barcode_image'):
                    raise ValueError("No barcode to share")
                img = self.original_barcode_image
                suffix = 'brcode'

            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp.name, 'PNG')
                tmp_path = tmp.name

            # Create a data URL
            with open(tmp_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            data_url = f"data:image/png;base64,{encoded_string}"
            
            # Create a simple window to display the shareable link
            share_window = tk.Toplevel(self.root)
            share_window.title(f"Share {image_type.upper()}")
            share_window.geometry("500x300")
            
            tk.Label(share_window, 
                    text=f"Copy this link to share the {image_type}:",
                    font=('Helvetica', 12)).pack(pady=10)
            
            # Create a text widget with the link
            link_text = tk.Text(share_window, height=3, wrap=tk.WORD, font=('Helvetica', 10))
            link_text.insert(tk.END, data_url)
            link_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
            
            # Add copy button
            copy_button = tk.Button(share_window, text="Copy Link", 
                                  command=lambda: self.copy_to_clipboard(data_url, share_window))
            copy_button.pack(pady=5)
            
            # Add open button
            open_button = tk.Button(share_window, text="Open in Browser", 
                                  command=lambda: webbrowser.open(data_url))
            open_button.pack(pady=5)
            
            # Clean up the temp file when window closes
            share_window.protocol("WM_DELETE_WINDOW", 
                                lambda: self.cleanup_temp_file(tmp_path, share_window))
            
            return data_url
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate share link: {str(e)}")
            if 'tmp_path' in locals():
                self.cleanup_temp_file(tmp_path)
            return None

    def copy_to_clipboard(self, text, window=None):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            if window:
                messagebox.showinfo("Copied", "Link copied to clipboard!", parent=window)
            else:
                messagebox.showinfo("Copied", "Link copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")

    def cleanup_temp_file(self, tmp_path, window=None):
        """Clean up temporary file and close window if provided"""
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            if window:
                window.destroy()
        except Exception as e:
            print(f"Error cleaning up temp file: {e}")

    def share_qr(self):
        """Share QR code with a copyable link"""
        if not hasattr(self, 'original_qr_image'):
            messagebox.showerror("Error", "No QR code to share")
            return
        self.generate_share_link('qr')

    def share_barcode(self):
        """Share Barcode with a copyable link"""
        if not hasattr(self, 'original_barcode_image'):
            messagebox.showerror("Error", "No barcode to share")
            return
        self.generate_share_link('barcode')