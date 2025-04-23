# -- mode: python ; coding: utf-8 --

import os
import sys
import tkinter
from PyInstaller.utils.hooks import collect_data_files

# Get the absolute path to the current directory
current_dir = os.path.abspath('.')

# Create a dummy Tkinter root to get the real tcl/tk paths
root = tkinter.Tk()
tcl_dir = root.tk.exprstring('$tcl_library')
tk_dir = root.tk.exprstring('$tk_library')
root.destroy()

block_cipher = None

# Add the parent directories for tcl/tk
tcl_dir = os.path.dirname(tcl_dir)
tk_dir = os.path.dirname(tk_dir)

# Verify and collect data files
datas = []
data_files = [
    ('app/inventory_data.json', 'app'),
    ('app/layout.txt', 'app'),
    ('app/required_layoyt.structure', 'app'),
    ('logo.ico', '.'),
]

# Only include files that exist
for src, dest in data_files:
    src_path = os.path.join(current_dir, src)
    if os.path.exists(src_path):
        datas.append((src_path, dest))
    else:
        print(f"Warning: File not found - {src_path}")

# Include all necessary modules 
hiddenimports = [
    'dotenv',
    'app.api_request.assign_inventory_api_request',
    'app.api_request.damage_inventory_api_request',
    'app.api_request.entry_inventory_api_request',
    'app.api_request.from_event_inventory_request',
    'app.api_request.to_event_inventory_request',
    'app.assign_inventory',
    'app.common_imports',
    'app.config',
    'app.damage_inventory',
    'app.from_event',
    'app.show_inventory',
    'app.to_event',
    'app.utils.field_validators',
    'app.utils.inventory_utils',
    'app.utils.loader',
    'app.widgets.inventory_combobox',
]

a = Analysis(
    [os.path.join(current_dir, 'app/entry_inventory.py')],
    pathex=[current_dir, os.path.join(current_dir, 'app')],
    binaries=[(tcl_dir, 'tcl'), (tk_dir, 'tk')],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Tagglabs_Inventory",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[os.path.join(current_dir, 'logo.ico')] if os.path.exists(os.path.join(current_dir, 'logo.ico')) else None,
    version=os.path.join(current_dir, 'version.txt') if os.path.exists(os.path.join(current_dir, 'version.txt')) else None
)