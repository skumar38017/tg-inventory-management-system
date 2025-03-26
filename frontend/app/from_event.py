#  frontend/app/from_event.py

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import platform
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
        
        # Maximize window
        self.maximize_window()
        
        logger.info("To Event window opened successfully")

    def maximize_window(self):
        try:
            self.window.state('zoomed')
        except tk.TclError:
            try:
                if platform.system() == 'Linux':
                    self.window.attributes('-zoomed', True)
                else:
                    self.window.attributes('-fullscreen', True)
            except:
                self.window.geometry("{0}x{1}+0+0".format(
                    self.window.winfo_screenwidth(),
                    self.window.winfo_screenheight()
                ))

    def setup_ui(self):
        """Set up all UI elements"""
        # Header section - Clock in row 0
        clock_frame = tk.Frame(self.window)
        clock_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=0)
        clock_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        clock_frame.grid_columnconfigure(1, weight=0)  # Center for clock
        clock_frame.grid_columnconfigure(2, weight=1)  # Right spacer

        # Clock in absolute center at top
        self.clock_label = tk.Label(clock_frame, font=('Helvetica', 8))
        self.clock_label.grid(row=0, column=1, sticky='n', pady=(0,0))
        self.update_clock()

        # Company info in row 1 (top-right corner)
        company_frame = tk.Frame(self.window)
        company_frame.grid(row=1, column=0, columnspan=2, sticky="e", padx=10, pady=0)
        company_frame.grid_columnconfigure(0, weight=1)  # Left spacer

        company_info = """Tagglabs Experiential Pvt. Ltd.
        Sector 49, Gurugram, Haryana 122018
        201, Second Floor, Eros City Square Mall
        Eros City Square
        098214 43358"""

        company_label = tk.Label(company_frame,
                               text=company_info,
                               font=('Helvetica', 7),
                               justify=tk.RIGHT)
        company_label.grid(row=0, column=1, sticky='ne', pady=(0,0))

        # Title label in row 2
        title_frame = tk.Frame(self.window)
        title_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        tk.Label(title_frame, 
               text="Items Going To Event",
               font=('Helvetica', 16, 'bold')).pack()

        # List display in row 3
        list_frame = tk.Frame(self.window)
        list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.event_listbox = tk.Listbox(
            list_frame,
            height=25,
            font=('Helvetica', 9),
            activestyle='none',
            selectbackground='#4a6984',
            selectforeground='white'
        )
        self.event_listbox.grid(row=0, column=0, sticky="nsew")

        list_scrollbar = tk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.event_listbox.yview
        )
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.event_listbox.config(yscrollcommand=list_scrollbar.set)

        # Bottom buttons in row 4
        bottom_frame = tk.Frame(self.window)
        bottom_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        # Action buttons on left
        action_frame = tk.Frame(bottom_frame)
        action_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Button(action_frame, 
                text="Mark Selected for Event", 
                command=self.mark_for_event,
                font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Return button on right
        return_button = tk.Button(bottom_frame, 
                                text="Return to Main", 
                                command=self.on_close,
                                font=('Helvetica', 10, 'bold'),
                                width=15)
        return_button.pack(side=tk.RIGHT, padx=10)

        # Grid configuration
        self.window.grid_rowconfigure(0, weight=0)  # Clock
        self.window.grid_rowconfigure(1, weight=0)  # Company info
        self.window.grid_rowconfigure(2, weight=0)  # Title
        self.window.grid_rowconfigure(3, weight=1)  # List
        self.window.grid_rowconfigure(4, weight=0)  # Buttons
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

    def mark_for_event(self):
        """Handle marking selected items for event"""
        selected = self.event_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select items from the list")
            return
        messagebox.showinfo("Info", f"{len(selected)} items marked for event")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing To Event window")
        self.window.destroy()
        self.parent.deiconify()  # Show parent window