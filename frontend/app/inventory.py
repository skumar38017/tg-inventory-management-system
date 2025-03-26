# frontend/app/inventory.py

import requests
from tkinter import messagebox

# Function to fetch inventory data from the backend
def fetch_inventory():
    try:
        response = requests.get("http://127.0.0.1:8000/inventory/")
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", "Failed to fetch inventory data")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Network error: {e}")
        return []

# Function to add a new inventory item
def add_inventory(item):
    try:
        response = requests.post("http://127.0.0.1:8000/inventory/", json=item)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Item added successfully")
        else:
            messagebox.showerror("Error", "Failed to add item")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Network error: {e}")