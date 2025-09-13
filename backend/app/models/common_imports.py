# ~/app/models/common_imports.py

# === Standard Library ===
import os
import uuid
import hashlib
import logging
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from typing import Dict, Any

# === SQLAlchemy ===
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Date,
    DateTime,
    Enum,
    Index,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import event, select

# === Third-Party Libraries ===
from barcode import Code128
from barcode.writer import ImageWriter

# === Local Application ===
from app.database.base import Base  # Assuming you have a base class for your models
