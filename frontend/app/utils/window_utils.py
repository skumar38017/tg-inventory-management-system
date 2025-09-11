#  frontend/app/utils/window_utils.py

# common/window_utils.py
import tkinter as tk
from tkinter import ttk
import platform
from datetime import datetime
import calendar

def maximize_window(window):
    """Maximize the window across different operating systems"""
    try:
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Try different methods to maximize window based on OS
        try:
            # First try standard zoomed state (works on Windows)
            window.state('zoomed')
        except tk.TclError:
            try:
                if platform.system() == 'Linux':
                    # For Linux, use the zoomed attribute
                    window.attributes('-zoomed', True)
                else:
                    # For other systems (Mac), try fullscreen
                    window.attributes('-fullscreen', True)
            except:
                # Fallback to setting geometry to screen dimensions
                window.geometry(f"{screen_width}x{screen_height}+0+0")

        # Additional measures to ensure full coverage
        try:
            # Update idle tasks to ensure window is rendered
            window.update_idletasks()
            
            # Check if window is actually covering the screen
            current_width = window.winfo_width()
            current_height = window.winfo_height()
            
            if current_width < screen_width or current_height < screen_height:
                # If not, explicitly set geometry
                window.geometry(f"{screen_width}x{screen_height}+0+0")
        except:
            pass

    except Exception as e:
        print(f"Window maximization error: {e}")
        # Fallback to basic geometry
        window.geometry("{0}x{1}+0+0".format(screen_width, screen_height))

def setup_clock_update(window, clock_label):
    """Setup automatic clock updates"""
    def update_clock():
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clock_label.config(text=now)
        window.after(1000, update_clock)
    update_clock()

def setup_window_closing(window, parent_window=None):
    """Standard window closing handler"""
    def on_close():
        if parent_window:
            parent_window.deiconify()
        window.destroy()
    window.protocol("WM_DELETE_WINDOW", on_close)

def open_calendar_window(parent_window, callback=None):
    """Open a standard calendar window with clear view"""
    cal_window = tk.Toplevel(parent_window)
    cal_window.title("Calendar")
    cal_window.geometry("400x350")
    cal_window.resizable(False, False)
    cal_window.configure(bg='white')
    
    # Center the window
    cal_window.transient(parent_window)
    cal_window.grab_set()
    
    # Current date
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    selected_date = now
    
    # Header frame
    header_frame = tk.Frame(cal_window, bg='#2c3e50', height=50)
    header_frame.pack(fill='x', pady=(0,10))
    header_frame.pack_propagate(False)
    
    # Navigation buttons and month/year display
    nav_frame = tk.Frame(header_frame, bg='#2c3e50')
    nav_frame.pack(expand=True, fill='both')
    
    prev_btn = tk.Button(nav_frame, text="◀", font=('Helvetica', 12, 'bold'),
                        bg='#34495e', fg='white', relief='flat', width=3)
    prev_btn.pack(side='left', padx=10, pady=10)
    
    month_year_label = tk.Label(nav_frame, font=('Helvetica', 14, 'bold'),
                               bg='#2c3e50', fg='white')
    month_year_label.pack(side='left', expand=True, pady=10)
    
    next_btn = tk.Button(nav_frame, text="▶", font=('Helvetica', 12, 'bold'),
                        bg='#34495e', fg='white', relief='flat', width=3)
    next_btn.pack(side='right', padx=10, pady=10)
    
    # Calendar frame
    cal_frame = tk.Frame(cal_window, bg='white')
    cal_frame.pack(expand=True, fill='both', padx=20, pady=10)
    
    # Days of week header
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for i, day in enumerate(days):
        day_label = tk.Label(cal_frame, text=day, font=('Helvetica', 10, 'bold'),
                           bg='#ecf0f1', fg='#2c3e50', width=5, height=2)
        day_label.grid(row=0, column=i, padx=1, pady=1, sticky='nsew')
    
    # Configure grid weights
    for i in range(7):
        cal_frame.grid_columnconfigure(i, weight=1)
    for i in range(7):
        cal_frame.grid_rowconfigure(i, weight=1)
    
    def update_calendar():
        # Clear existing day buttons
        for widget in cal_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
        
        # Update month/year label
        month_year_label.config(text=f"{calendar.month_name[current_month]} {current_year}")
        
        # Get calendar data
        cal = calendar.monthcalendar(current_year, current_month)
        
        # Create day buttons
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days from other months
                    empty_label = tk.Label(cal_frame, text="", bg='white', width=5, height=2)
                    empty_label.grid(row=week_num, column=day_num, padx=1, pady=1, sticky='nsew')
                else:
                    # Check if this is today
                    is_today = (day == now.day and current_month == now.month and current_year == now.year)
                    
                    bg_color = '#3498db' if is_today else '#ffffff'
                    fg_color = 'white' if is_today else '#2c3e50'
                    
                    day_btn = tk.Button(cal_frame, text=str(day),
                                      font=('Helvetica', 10, 'bold' if is_today else 'normal'),
                                      bg=bg_color, fg=fg_color, relief='flat',
                                      width=5, height=2,
                                      command=lambda d=day: select_date(d))
                    day_btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky='nsew')
    
    def select_date(day):
        nonlocal selected_date
        selected_date = datetime(current_year, current_month, day)
        if callback:
            callback(selected_date)
        cal_window.destroy()
    
    def prev_month():
        nonlocal current_month, current_year
        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1
        update_calendar()
    
    def next_month():
        nonlocal current_month, current_year
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
        update_calendar()
    
    prev_btn.config(command=prev_month)
    next_btn.config(command=next_month)
    
    # Bottom buttons
    button_frame = tk.Frame(cal_window, bg='white')
    button_frame.pack(fill='x', padx=20, pady=10)
    
    today_btn = tk.Button(button_frame, text="Today", font=('Helvetica', 10, 'bold'),
                         bg='#27ae60', fg='white', relief='flat', width=10,
                         command=lambda: select_date(now.day) if current_month == now.month and current_year == now.year else None)
    today_btn.pack(side='left')
    
    cancel_btn = tk.Button(button_frame, text="Cancel", font=('Helvetica', 10, 'bold'),
                          bg='#95a5a6', fg='white', relief='flat', width=10,
                          command=cal_window.destroy)
    cancel_btn.pack(side='right')
    
def create_date_range_picker(parent_frame, bg_color='#ecf0f1', start_column=0, row=0):
    """Create standardized From Date and To Date picker with larger dropdown"""
    from tkcalendar import DateEntry
    from datetime import datetime
    
    # From Date
    tk.Label(parent_frame, text="From Date:", font=('Helvetica', 10, 'bold'), 
            bg=bg_color, fg='#2c3e50').grid(row=row, column=start_column, padx=5, sticky='e')
    
    from_date_entry = DateEntry(
        parent_frame,
        width=15,
        background='#3498db',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        font=('Helvetica', 10),
        calendar_font=('Helvetica', 12),
        calendar_width=300,
        calendar_height=250
    )
    from_date_entry.grid(row=row, column=start_column+1, padx=5, sticky='w')
    from_date_entry.set_date(datetime.now().replace(day=1))
    
    # To Date
    tk.Label(parent_frame, text="To Date:", font=('Helvetica', 10, 'bold'), 
            bg=bg_color, fg='#2c3e50').grid(row=row, column=start_column+2, padx=5, sticky='e')
    
    to_date_entry = DateEntry(
        parent_frame,
        width=15,
        background='#3498db',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        font=('Helvetica', 10),
        calendar_font=('Helvetica', 12),
        calendar_width=300,
        calendar_height=250
    )
    to_date_entry.grid(row=row, column=start_column+3, padx=5, sticky='w')
    to_date_entry.set_date(datetime.now())
    
    return from_date_entry, to_date_entry

    # Initialize calendar
    update_calendar()
    
    return cal_window