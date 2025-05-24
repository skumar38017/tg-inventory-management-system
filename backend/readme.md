# 🗃️ TG Inventory Management System - Backend

This is the Backend component of the TG Inventory Management System, developed by Tagglabs. It is a Python-based application designed to manage inventory operations like entry, assignment, tracking, and event-based handling. The backend is modular and organized to support scalability, maintainability, and integration with external systems like Google Sheets.

---

## 📁 Project Structure

```plaintext
backend/
├── app/
│   ├── barcode_route/               # Routes related to barcode and QR code operations
│   ├── credentials/                # Google credentials and user auth files
│   ├── curd/                       # Business logic (CRUD operations)
│   │   └── instructions/           # Instruction sets (TBD)
│   ├── database/                   # Database connection and Redis client
│   ├── interface/                  # Interface logic for each inventory operation
│   ├── Middleware/                 # Middleware logic
│   ├── models/                     # Pydantic and ORM models
│   ├── public/                     # Static assets (logos, icons)
│   ├── routers/                    # FastAPI routers
│   ├── schema/                     # Pydantic schemas
│   ├── services/                   # Barcode/QR services
│   ├── templates/                  # HTML templates
│   ├── utils/                      # Utilities like barcode generation, validators, etc.
│   ├── api_gateways.py             # API gateway logic
│   ├── config.py                   # Configuration settings
│   ├── dependencies.py             # Dependency injections
│   ├── google_sheets_auth_setup.py # Google Sheets OAuth setup
│   ├── main.py                     # FastAPI main entrypoint
│   └── __init__.py
├── command.txt                     # Command references
├── readme.md                       # Project documentation
└── requirements.txt                # Python package requirements
```

# 🚀 Features

* ✅ Inventory Entry Management: `Add` and `update` inventory records.

* ✅ Inventory Assignment: `Assign items` to users or locations.

* ✅ Damage Tracking: Mark items as damaged or unusable.

* ✅ Event-Based Movement: `Track` inventory dispatched to or returned from events.

* ✅ QR/Barcode Integration: `Scan` and `generate` codes for inventory tracking.

* ✅ Google Sheets Sync: `Integrate` and sync with `Google` Sheets (via Redis).

* ✅ Modular Architecture: Logical separation for models, routes, services, and interfaces.



## 🛠️ Setup Guide

## Step 1: Clone the Repository

````bash
git clone [Repo](https://github.com/skumar38017/tg-inventory-management-system.git)
cd tg-inventory-management-system
````

## Step 2: Setup Database and Redis Server (Optional) if Required

✅ For `Linux`

1. ### Install PostgreSQL

```bash
sudo apt-get install postgresql postgresql-contrib
```

2. ### Create a new PostgreSQL user

```bash
sudo -u postgres createuser -s tg-inventory
```

3. ### Create a new PostgreSQL database

```bash
sudo -u postgres createdb -O tg-inventory tg-inventory
```

4. ### Connect to PostgreSQL

```bash
psql -h localhost -p 5432 -U postgres
```

5. ### Inside psql:

```bash
CREATE ROLE "tg-inventory" WITH LOGIN PASSWORD 'tg-inventory';
CREATE DATABASE "tg-inventory" OWNER "tg-inventory";
GRANT ALL PRIVILEGES ON DATABASE "tg-inventory" TO "tg-inventory";

ALTER ROLE "tg-inventory" WITH
  SUPERUSER
  CREATEDB
  CREATEROLE
  REPLICATION
  BYPASSRLS;
```

6. ### Connect to PostgreSQL Database

```bash
psql -h localhost -p 5432 -U tg-inventory -d tg-inventory
```

7. ### Install Redis

```bash
sudo apt-get install redis-server
```

8. ### Connect to Redis

```bash
redis-cli -h localhost -p 6379 -a Neon-Studioz-Holi-T25
```

9. ### Flush Redis

```bash
redis-cli -h localhost -p 6379 -a Neon-Studioz-Holi-T25 FLUSHDB
```

✅ For `Windows`

1. ### Install PostgreSQL

Install PostgreSQL from [PostgreSQL](https://www.postgresql.org/download/windows/) website.

2. ### Create a new PostgreSQL user
```cmd
sudo -u postgres createuser -s tg-inventory
```

3. ### Create a new PostgreSQL database
```cmd
sudo -u postgres createdb -O tg-inventory tg-inventory
```

4. ### Connect to PostgreSQL
```cmd
psql -h localhost -p 5432 -U postgres
```

5. ### Inside psql:
```cmd
CREATE ROLE "tg-inventory" WITH LOGIN PASSWORD 'tg-inventory';
CREATE DATABASE "tg-inventory" OWNER "tg-inventory";
GRANT ALL PRIVILEGES ON DATABASE "tg-inventory" TO "tg-inventory";

ALTER ROLE "tg-inventory" WITH
  SUPERUSER
  CREATEDB
  CREATEROLE
  REPLICATION
  BYPASSRLS;
```

6. ### Connect to PostgreSQL Database
```cmd
psql -h localhost -p 5432 -U tg-inventory -d tg-inventory
```

7. ### Install Redis for Windows
Redis does not officially support Windows, but you can use:

* (i) the Windows Subsystem for Linux (WSL) to run Redis on Windows

* (ii) the Redis Desktop Manager to run Redis on Windows

* (iii) the Redis Command Line Interface (CLI) to run Redis on Windows

first, install the Redis Desktop Manager from [Redis](https://redis.com/try-free/) website.

second, run the Redis server with the following command:

`redis-server --service-install`

third, open the Redis Desktop Manager and add a new server with the following settings:

- Server type: Standalone
- Server name: Redis
- Server IP: 127.0.0.1
- Server port: 6379
- Server password: Neon-Studioz-Holi-T25

fourth, open the Redis Desktop Manager and click on the "Redis" server to connect to the server.

fifth, run the following command in the Redis Desktop Manager to flush the Redis database:

8. ### Connect to Redis
```cmd
redis-cli -h localhost -p 6379 -a Neon-Studioz-Holi-T25
```

9. ### Flush Redis   
```cmd
redis-cli -h localhost -p 6379 -a Neon-Studioz-Holi-T25 FLUSHDB
```

## Step 3: Set Up Python Environment
✅ For `Linux`

1. Install Python 3.11:

```bash
sudo apt install python3.11
sudo apt install python-is-python3 -y
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
    cd tg-inventory-management-system/backend
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

***Setup `.env` file according to ```.env.sample```***

## Step 4: Migrate Database
1. Generate and apply new migrations and verify into database

```bash
export PYTHONPATH=$(pwd)
PYTHONPATH=./ alembic revision --autogenerate -m "Initial migration"
PYTHONPATH=./ alembic upgrade head
```
2. ### Connect to PostgreSQL Database

```bash
psql -h localhost -p 5432 -U tg-inventory -d tg-inventory
```
3. ### Inside psql to check migrate table

```bash
\dt
```

## Step 5: Run the Backend server

```bash
cd tg-inventory-management-system
export PYTHONPATH=$(pwd)
uvicorn backend.app.main:app --reload
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

# 🗃️ TG Inventory Management System - Backend

This is the **Backend** component of the **TG Inventory Management System**, developed by **Tagglabs**. It is a Python-based desktop application designed to manage inventory-related operations such as entry, assignment, tracking, and event-based handling.

---        

