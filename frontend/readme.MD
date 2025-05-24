# 🗃️ TG Inventory Management System - Frontend

This is the `**Frontend**` component of the **TG Inventory Management System**, developed by **Tagglabs**. It is a Python-based desktop application designed to manage inventory-related operations such as entry, assignment, tracking, and event-based handling.

---

## 📁 Project Structure

```plaintext
frontend/
├── app/
│   ├── api_request/           # API request handlers for inventory operations
│   ├── utils/                 # Utility functions and helpers
│   ├── widgets/               # Custom UI components
│   ├── assign_inventory.py    # Inventory assignment UI logic
│   ├── damage_inventory.py    # Track and mark damaged inventory
│   ├── entry_inventory.py     # UI for adding new inventory entries
│   ├── from_event.py          # Track inventory returned from events
│   ├── to_event.py            # Track inventory dispatched to events
│   ├── image_view.py          # View inventory images
│   ├── reveal_qr_barcode_window.py  # QR/Barcode scanner window
│   └── inventory_data.json    # Local inventory data store
├── Dockerfile                 # Docker setup
├── docker-entrypoint.sh       # Docker entrypoint script
├── requirements.txt           # Python package requirements
├── frontend.spec              # PyInstaller build specification
├── logo.ico                   # Application icon
├── logo.webp                  # Web logo
├── favicon.ico                # Favicon for web-based view
├── version.txt                # Application versioning
├── command.txt                # Reference command list
└── README.md                  # This documentation file
```

# 🚀 Features

* Inventory Entry Management: `Add` and `Update` inventory records easily.

* Inventory Assignment: `Assign inventory` to users or locations.

* Damage Tracking: `Mark` inventory items as damaged.

* Event Tracking: `Manage inventory dispatched` to or returned from events.

* QR/Barcode Integration: `Scan codes` to `track` inventory.

* Local JSON Support: Store and load data from local JSON files.

* Modular Utilities: Utilities for validation, loading, and UI management.


# 🛠️ Setup Guide

##### Step 1: Clone the Repository

````bash
git clone [Repo](https://github.com/skumar38017/tg-inventory-management-system.git)
cd tg-inventory-management-system
````
##### Step 2: Set Up Python Environment
✅ For `Linux`

1. Install Python 3.11:

```bash
sudo apt install python3.11
```

2. Create a virtual environment:

```bash
python3 -m venv venv
```

3. `Activate` the virtual environment:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

✅ For `Windows`

1. Install `Python 3.11` from [Python 3.11](https://www.python.org/downloads/windows/) website.

2. Navigate to the project directory:
    ```bash
    cd tg-inventory-management-system/frontend
    ```
3. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
4. `Activate` the virtual environment:

    ```cmd
    venv\Scripts\activate
    ```
5. Install dependencies:

    ```cmd
    pip install -r requirements.txt
    ```

##### Step 3: Run the Application

```bash
python app/entry_inventory.py
```
## 📄 License

This project is proprietary and intended for internal use at Tagglabs. Redistribution is not permitted without prior written permission.

## 👨‍💻 Author & Maintainer

Tagglabs

📧 info@tagglabs.in

🌐 [`Tagglabs`](https://tagglabs.in)

## 🙌 Contributing

At the moment, this project is not accepting public contributions. For inquiries or feature requests, please contact the maintainers directly.

---

Let me know if you'd like a GitHub-flavored version with badges (e.g., Python version, license, Docker ready, etc.), or if you want me to write a `CONTRIBUTING.md` or `LICENSE` file.

---

# 🗃️ TG Inventory Management System - Frontend

This is the **Frontend** component of the **TG Inventory Management System**, developed by **Tagglabs**. It is a Python-based desktop application designed to manage inventory-related operations such as entry, assignment, tracking, and event-based handling.

---        

