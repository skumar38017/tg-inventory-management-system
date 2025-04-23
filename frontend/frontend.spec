# -- mode: python ; coding: utf-8 --

import os
import sys
import tkinter
from PyInstaller.utils.hooks import collect_data_files

# Get the current working directory (alternative to __file__)
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

# Add the app directory to the path
sys.path.append(current_dir)

# Collect all necessary data files including .env
datas = [
    (os.path.join(current_dir, 'app/inventory_data.json'), 'app'),
    (os.path.join(current_dir, 'app/logo.webp'), 'app'),
    (os.path.join(current_dir, 'app/layout.txt'), 'app'),
    (os.path.join(current_dir, 'app/required_layoyt.structure'), 'app'),
    (os.path.join(current_dir, 'logo.ico'), '.'),
]

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
    name="Tagglabs_Inventory",  # Changed space to underscore for better compatibility
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
    icon=[os.path.join(current_dir, 'logo.ico')],
    version=os.path.join(current_dir, 'version.txt')
)