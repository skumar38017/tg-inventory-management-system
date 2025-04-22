#  app.utils.loader.py
import tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import time
import queue
import threading
from itertools import cycle
from PIL import Image, ImageTk
import io
import base64

# Enhanced loading indicator with animation
class EnhancedLoader:
    def __init__(self, parent, message="Processing..."):
        self.parent = parent
        self.loader_window = tk.Toplevel(parent)
        self.loader_window.title("Please Wait")
        self.loader_window.resizable(False, False)
        
        # Window styling
        self.loader_window.configure(bg='#f5f5f5')
        self.loader_window.attributes('-alpha', 0.0)  # Start transparent
        
        # Create loading frame
        frame = ttk.Frame(self.loader_window, padding=(20, 10))
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Loading message
        self.message_var = tk.StringVar(value=message)
        ttk.Label(frame, textvariable=self.message_var, 
                 font=('Arial', 10), justify=tk.CENTER).pack(pady=(0, 15))
        
        # Animated progress bar
        self.progress = ttk.Progressbar(frame, mode='indeterminate', 
                                      length=200, style='custom.Horizontal.TProgressbar')
        self.progress.pack(pady=5)
        
        # Percentage label
        self.percent_var = tk.StringVar(value="0%")
        ttk.Label(frame, textvariable=self.percent_var, 
                 font=('Arial', 8)).pack()
        
        # Loading animation frames (simulated)
        self.animation_frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        self.anim_index = 0
        self.anim_cycle = cycle(self.animation_frames)
        
        # Center and fade in
        self.center_window()
        self.fade_in()
        
        # Make it modal
        self.loader_window.grab_set()
        self.loader_window.transient(parent)
        
        # Start animations
        self.animate_spinner()
        self.progress.start()
    
    def center_window(self):
        self.loader_window.update_idletasks()
        width = self.loader_window.winfo_width()
        height = self.loader_window.winfo_height()
        x = (self.loader_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.loader_window.winfo_screenheight() // 2) - (height // 2)
        self.loader_window.geometry(f"+{x}+{y}")
    
    def fade_in(self):
        alpha = self.loader_window.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.05
            self.loader_window.attributes('-alpha', alpha)
            self.loader_window.after(20, self.fade_in)
    
    def animate_spinner(self):
        spinner_char = next(self.anim_cycle)
        current_msg = self.message_var.get().split("]")[-1].strip()
        self.message_var.set(f"[{spinner_char}] {current_msg}")
        self.loader_window.after(100, self.animate_spinner)
    
    def update_progress(self, percent):
        self.percent_var.set(f"{percent}%")
        self.progress['value'] = percent
    
    def close(self):
        self.fade_out()
    
    def fade_out(self):
        alpha = self.loader_window.attributes('-alpha')
        if alpha > 0:
            alpha -= 0.05
            self.loader_window.attributes('-alpha', alpha)
            self.loader_window.after(20, self.fade_out)
        else:
            self.loader_window.destroy()

# Demo application
class BufferLoaderDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Buffer & Loader Demo")
        self.root.geometry("600x400")
        self.style = ttk.Style()
        self.configure_styles()
        
        self.create_widgets()
        self.buffer.update_visuals = True
    
    def configure_styles(self):
        self.style.configure('custom.Horizontal.TProgressbar', 
                            background='#4CAF50',
                            troughcolor='#E0E0E0',
                            bordercolor='#E0E0E0',
                            lightcolor='#4CAF50',
                            darkcolor='#2E7D32')
        
        self.style.configure('TButton', padding=6, font=('Arial', 9))
        self.style.map('TButton',
                      foreground=[('active', '!disabled', 'black')],
                      background=[('active', '#64B5F6')])
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="Add Item", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Process Item", command=self.process_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show Loader", command=self.show_loader).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Buffer", command=self.clear_buffer).pack(side=tk.LEFT, padx=5)
        
        # Buffer visualization
        ttk.Label(main_frame, text="Buffer Visualization", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.X, pady=(0, 10))
        
        # Log output
        ttk.Label(main_frame, text="Activity Log", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.log_text = tk.Text(main_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def add_item(self):
        item_count = self.buffer.queue.qsize()
        if item_count < self.buffer.max_size:
            item = {'id': item_count + 1, 'data': f"Data-{item_count + 1}"}
            if self.buffer.add_item(item):
                self.log_message(f"✅ Added item: {item['data']}")
            else:
                self.log_message("❌ Failed to add item (queue full")