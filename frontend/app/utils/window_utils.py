#  frontend/app/utils/window_utils.py

# common/window_utils.py
import tkinter as tk
import platform
from datetime import datetime

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