# backend/app/routers/inventory.py

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

# Function to Search for an inventory item
def search_inventory(query):
    try:
        response = requests.get(f"http://127.0.0.1:8000/inventory/?query={query}")
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", "Failed to search for item")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Network error: {e}")
        return []
    
#  Function to get the total number of items in the inventory
def get_inventory_by_date_range ():
    try:
        response = requests.get("http://127.0.0.1:8000/inventory/date_range/")
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", "Failed to fetch inventory data")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Network error: {e}")
        return []