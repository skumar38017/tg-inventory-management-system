#  frontend/app/from_inventory.py

# frontend/app/to_event.py

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FromEventWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs - To Event")
        
        # Hide parent window (optional)
        self.parent.withdraw()
        
        # Setup the window
        self.setup_ui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Focus on this window
        self.window.focus_set()
        
        logger.info("To Event window opened successfully")

    def setup_ui(self):
        """Set up all UI elements"""
        # Header
        header_frame = tk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Clock
        self.clock_label = tk.Label(header_frame, font=('Helvetica', 8))
        self.clock_label.pack(side=tk.LEFT)
        self.update_clock()
        
        # Company info
        company_frame = tk.Frame(header_frame)
        company_frame.pack(side=tk.RIGHT)
        
        company_info = """Tagglabs Experiential Pvt. Ltd.
Sector 49, Gurugram, Haryana 122018"""
        
        tk.Label(company_frame, text=company_info, 
                font=('Helvetica', 7), justify=tk.RIGHT).pack()
        
        # Main content
        content_frame = tk.Frame(self.window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(content_frame, 
                text="Items Going To Event",
                font=('Helvetica', 16, 'bold')).pack()
        
        # Add your specific To Event content here
        
        # Bottom buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Return to Main", 
                command=self.on_close,
                font=('Helvetica', 10)).pack(side=tk.RIGHT)

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing To Event window")
        self.parent.deiconify()  # Show parent window
        self.window.destroy()