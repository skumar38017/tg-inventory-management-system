#!/usr/bin/env python3
"""Launcher script for entry_inventory.py - redirects to homePage/entry_inventory.py"""
import os
import sys

# Get the directory of this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the app directory to Python path
sys.path.insert(0, current_dir)

# Import and run the main module from homePage
from homePage.entry_inventory import main

if __name__ == "__main__":
    main()
