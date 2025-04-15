#  frontend/app/widgets/inventory_combobox.py
import requests
from typing import List, Dict
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ..config import make_api_request
from ..utils.inventory_utils import format_wastage_inventory_item

logger = logging.getLogger(__name__)

class InventoryComboBox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<KeyRelease>', self._on_keyrelease)
        self.bind('<<ComboboxSelected>>', self._on_select)
        self._inventory_data = []
        self._last_search = ""
        self._typing = False
        
    def _on_keyrelease(self, event):
        """Handle key releases while maintaining natural typing flow"""
        if event.keysym in ('BackSpace', 'Delete') or len(event.keysym) == 1:
            current = self.get()
            if current != self._last_search:
                self._typing = True
                self._last_search = current
                
                # Save cursor position
                cursor_pos = self.index(tk.INSERT)
                
                # Perform search in background
                self.after(100, lambda: self._update_suggestions(current, cursor_pos))
                
    def _update_suggestions(self, search_term: str, cursor_pos: int):
        """Update suggestions without interfering with typing"""
        try:
            items = self._fetch_inventory_items(search_term)
            self._inventory_data = items
            names = [item['inventory_name'] for item in items if item['inventory_name']]
            
            # Update dropdown values
            self['values'] = names
            
            # Only show dropdown if there are matches
            if names and search_term:
                self._show_dropdown()
                
            # Restore cursor position and typing state
            self.icursor(cursor_pos)
            self.focus_set()
            self._typing = False
            
        except Exception as e:
            logging.error(f"Error searching inventory: {e}")
            messagebox.showerror("Error", f"Failed to search inventory: {e}")
                
    def _show_dropdown(self):
        """Show dropdown without taking focus"""
        if self._typing:
            return
            
        # Temporarily disable typing flag to allow dropdown
        self._typing = False
        self.event_generate('<Down>')
        self._typing = True
        
    def _on_select(self, event):
        """Handle selection from dropdown"""
        if not self._typing:
            selected_index = self.current()
            if 0 <= selected_index < len(self._inventory_data):
                selected_item = self._inventory_data[selected_index]
                print(f"Selected: {selected_item['inventory_name']} (ID: {selected_item['inventory_id']})")
            
    def get_selected_item(self) -> Dict:
        """Get the full data for the currently selected item"""
        selected_index = self.current()
        if 0 <= selected_index < len(self._inventory_data):
            return self._inventory_data[selected_index]
        return None
    
    def _fetch_inventory_items(self, search_term: str = None) -> List[Dict]:
        """Search inventory items from API"""
        try:
            params = {'inventory_name': search_term, 'skip': 0} if search_term else {}
            response = make_api_request(
                "GET", 
                "inventory-combobox/",
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            return [format_wastage_inventory_item(item) for item in data.get('items', [])]
                
        except requests.exceptions.Timeout:
            error_msg = "Search timed out. Please try again later."
            logger.error(error_msg)
            messagebox.showerror("Timeout Error", error_msg)
            return []
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to search inventory: {e}"
            logger.error(error_msg)
            messagebox.showerror("API Error", error_msg)
            return []
    
#  Drop Down search list option  ComboBox Widget for damage inventory directly from redis with related details of `inventory_id`
def inventory_ComboBox(search_term: str = None) -> List[Dict]:
    """Search damage inventory from Redis by inventory name across multiple key patterns"""
    try:
        params = {'inventory_name': search_term, 'skip': 0} if search_term else {}
        response = make_api_request(
            "GET", 
            "inventory-combobox/",
            params=params,
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        return [format_wastage_inventory_item(item) for item in data.get('items', [])]
            
    except requests.exceptions.Timeout:
        error_msg = "Search timed out. Please try again later."
        logger.error(error_msg)
        messagebox.showerror("Timeout Error", error_msg)
        return []
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to search inventory: {e}"
        logger.error(error_msg)
        messagebox.showerror("API Error", error_msg)
        return []