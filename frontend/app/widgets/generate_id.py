#  frontend/app/widgets/generate_id.py
import random
import string
import tkinter as tk

def generate_inventory_id():
    """Generate inventory ID starting with INV followed by 6 random digits"""
    random_number = random.randint(100000, 999999)
    return f"INV{random_number}"

def generate_product_id():
    """Generate product ID starting with PRD followed by 6 random digits"""
    random_number = random.randint(100000, 999999)
    return f"PRD{random_number}"
