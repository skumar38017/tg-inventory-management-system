# backend/app/config.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.ext.declarative import declarative_base

load_dotenv() 
Base = declarative_base() 

# Google Sheets Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Redis Configuration
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "")  # empty fallback
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

if REDIS_USERNAME:
    REDIS_URL = f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Email Settings
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = bool(os.getenv("EMAIL_USE_TLS", True))
EMAIL_USE_SSL = bool(os.getenv("EMAIL_USE_SSL", False))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "your_email@gmail.com")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "your_email@gmail.com")

# Optional: PostgreSQL connection details for admin operations (if separate)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
SYNC_DB_URL=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
ASYNC_DB_URL=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Build the full path to credentials file
credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT", "/app/credentials/users/office-inventory-457815-933d2b7634a8.json")
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, credentials_path)

# Verify the file exists at startup
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise ValueError(f"Google credentials file not found at: {SERVICE_ACCOUNT_FILE}")

SPREADSHEET_URL = os.getenv("SPREADSHEET_URL")
SHEET_NAME = os.getenv("SHEET_NAME", "testing")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_ARN = os.getenv("AWS_ARN")

# Folder configurations
AWS_S3_BUCKET_FOLDER_PATH_QR = os.getenv("AWS_S3_BUCKET_FOLDER_PATH_QR", "qrcode")
AWS_S3_BUCKET_FOLDER_PATH_BARCODE = os.getenv("AWS_S3_BUCKET_FOLDER_PATH_BARCODE", "barcode")



# Handle multiple PUBLIC_API_URL options
PUBLIC_API_URLS = [
    url.strip() 
    for url in os.getenv('PUBLIC_API_URL', 'http://localhost:8000').split(',')
    if url.strip()
]
PUBLIC_API_URL = PUBLIC_API_URLS[0] if PUBLIC_API_URLS else "http://localhost:8000"  # Default to first URL

# Server IP Configuration
SERVER_IP = [
    url.strip() 
    for url in os.getenv('PUBLIC_API_URL', 'http://localhost:8000').split(',')
    if url.strip()
]
SERVER_IP = SERVER_IP[0]  # Default to first URL

BASE_URL = [
    url.strip() 
    for url in os.getenv('PUBLIC_API_URL', 'http://localhost:8000').split(',')
    if url.strip()
]
BASE_URL = BASE_URL[0]  # Default to first URL

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT=int(os.getenv("PORT", 8000))