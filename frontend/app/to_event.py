import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import platform
import logging

logger = logging.getLogger(__name__)

class ToEventWindow:
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

        # Title section in row 2
        title_frame = tk.Frame(self.window)
        title_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Centered company name
        tk.Label(title_frame, 
               text="Tagglabs Experiential Pvt. Ltd",
               font=('Helvetica', 14, 'bold')).pack()
        
        # Centered inventory list title
        tk.Label(title_frame, 
               text="INVENTORY LIST",
               font=('Helvetica', 12, 'bold')).pack()

        # Information fields in row 3
        info_frame = tk.Frame(self.window)
        info_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Employee Name and Location
        tk.Label(info_frame, text="Employee Name", font=('Helvetica', 9)).grid(row=0, column=0, sticky='e', padx=5)
        self.employee_name = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.employee_name.grid(row=0, column=1, sticky='w', padx=5)
        
        tk.Label(info_frame, text="Location", font=('Helvetica', 9)).grid(row=0, column=2, sticky='e', padx=5)
        self.location = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.location.grid(row=0, column=3, sticky='w', padx=5)
        
        # Client Name and Setup Date
        tk.Label(info_frame, text="Client Name", font=('Helvetica', 9)).grid(row=1, column=0, sticky='e', padx=5)
        self.client_name = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.client_name.grid(row=1, column=1, sticky='w', padx=5)
        
        tk.Label(info_frame, text="Setup Date", font=('Helvetica', 9)).grid(row=1, column=2, sticky='e', padx=5)
        self.setup_date = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.setup_date.grid(row=1, column=3, sticky='w', padx=5)
        
        # Project Name and Event Date
        tk.Label(info_frame, text="Project Name", font=('Helvetica', 9)).grid(row=2, column=0, sticky='e', padx=5)
        self.project_name = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.project_name.grid(row=2, column=1, sticky='w', padx=5)
        
        tk.Label(info_frame, text="Event Date", font=('Helvetica', 9)).grid(row=2, column=2, sticky='e', padx=5)
        self.event_date = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.event_date.grid(row=2, column=3, sticky='w', padx=5)
        
        # Separator line
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # Inventory table in row 5
        table_frame = tk.Frame(self.window)
        table_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Create a canvas and scrollbar for the table
        canvas = tk.Canvas(table_frame)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Table headers
        headers = [
            "Zone/Activity", "Sr. No.", "Inventory", "Description/Specifications",
            "Quantity", "Comments", "Total", "Units", 
            "Per Unit Power Consumption (Watt/H)", "Total Power Consumption (Watt)",
            "Status (purchased/not purchased)", "POC"
        ]

        for col, header in enumerate(headers):
            tk.Label(scrollable_frame, text=header, font=('Helvetica', 9, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")

        # Create entry fields for each column
        self.table_entries = []
        for row in range(1, 6):  # Create 5 empty rows
            row_entries = []
            for col in range(len(headers)):
                if col == 4 or col == 6 or col == 7 or col == 8 or col == 9:  # Numeric fields
                    entry = tk.Entry(scrollable_frame, font=('Helvetica', 9), width=15)
                else:
                    entry = tk.Entry(scrollable_frame, font=('Helvetica', 9), width=20)
                entry.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                row_entries.append(entry)
            self.table_entries.append(row_entries)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bottom buttons in row 6
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Remove row button (added before Add Row)
        remove_row_btn = tk.Button(button_frame, text="Remove Row", command=self.remove_table_row,
                                 font=('Helvetica', 10, 'bold'))
        remove_row_btn.pack(side=tk.LEFT, padx=5)

        # Add row button
        add_row_btn = tk.Button(button_frame, text="Add Row", command=self.add_table_row,
                              font=('Helvetica', 10, 'bold'))
        add_row_btn.pack(side=tk.LEFT, padx=5)

        # Submit button
        submit_btn = tk.Button(button_frame, text="Submit", command=self.submit_form,
                             font=('Helvetica', 10, 'bold'))
        submit_btn.pack(side=tk.LEFT, padx=5)

        # Return button on right
        return_button = tk.Button(button_frame, 
                                text="Return to Main", 
                                command=self.on_close,
                                font=('Helvetica', 10, 'bold'),
                                width=15)
        return_button.pack(side=tk.RIGHT, padx=5)

        # Grid configuration
        self.window.grid_rowconfigure(0, weight=0)  # Clock
        self.window.grid_rowconfigure(1, weight=0)  # Company info
        self.window.grid_rowconfigure(2, weight=0)  # Title
        self.window.grid_rowconfigure(3, weight=0)  # Info fields
        self.window.grid_rowconfigure(4, weight=0)  # Separator
        self.window.grid_rowconfigure(5, weight=1)  # Table
        self.window.grid_rowconfigure(6, weight=0)  # Buttons
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

    def add_table_row(self):
        """Add a new row to the table"""
        current_rows = len(self.table_entries)
        headers = [
            "Zone/Activity", "Sr. No.", "Inventory", "Description/Specifications",
            "Quantity", "Comments", "Total", "Units", 
            "Per Unit Power Consumption (Watt/H)", "Total Power Consumption (Watt)",
            "Status (purchased/not purchased)", "POC"
        ]
        
        row_entries = []
        for col in range(len(headers)):
            if col == 4 or col == 6 or col == 7 or col == 8 or col == 9:  # Numeric fields
                entry = tk.Entry(self.table_entries[0][0].master, font=('Helvetica', 9), width=15)
            else:
                entry = tk.Entry(self.table_entries[0][0].master, font=('Helvetica', 9), width=20)
            entry.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
            row_entries.append(entry)
        self.table_entries.append(row_entries)

    def remove_table_row(self):
        """Remove the last row from the table"""
        if len(self.table_entries) <= 1:  # Keep at least one row
            messagebox.showwarning("Warning", "Cannot remove the last row")
            return
            
        last_row = self.table_entries.pop()
        for entry in last_row:
            entry.destroy()

    def submit_form(self):
        """Handle form submission"""
        # Validate required fields
        if not self.employee_name.get() or not self.client_name.get():
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return
            
        # Process the data
        data = {
            'employee_name': self.employee_name.get(),
            'location': self.location.get(),
            'client_name': self.client_name.get(),
            'setup_date': self.setup_date.get(),
            'project_name': self.project_name.get(),
            'event_date': self.event_date.get(),
            'inventory_items': []
        }
        
        for row in self.table_entries:
            item = {
                'zone_activity': row[0].get(),
                'sr_no': row[1].get(),
                'inventory': row[2].get(),
                'description': row[3].get(),
                'quantity': row[4].get(),
                'comments': row[5].get(),
                'total': row[6].get(),
                'units': row[7].get(),
                'power_per_unit': row[8].get(),
                'total_power': row[9].get(),
                'status': row[10].get(),
                'poc': row[11].get()
            }
            data['inventory_items'].append(item)
        
        messagebox.showinfo("Success", "Form submitted successfully")
        logger.info(f"Form submitted: {data}")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing To Event window")
        self.window.destroy()
        self.parent.deiconify()  # Show parent window