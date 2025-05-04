# backend/app/utils/common_imports.py

# Standard Library Imports
import os
import re
import json
import uuid
import logging
import uvicorn
import random
import asyncio
import base64
import pickle
import hashlib
from enum import Enum
from io import BytesIO
from typing import (
    Any, Optional, List, Dict, Union, 
    Tuple, Type, Generic, TypeVar
)
from fastapi.routing import APIRoute
from datetime import datetime, date, time, timedelta, timezone

# Third-Party Imports
from fastapi import (
    APIRouter, FastAPI, HTTPException, Depends,
    Request, Response, Query, UploadFile, File
)
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pydantic import (
    BaseModel, field_validator, ConfigDict, Field, ValidationInfo,
    model_validator, field_serializer, ValidationError
)
from sqlalchemy import (
    select, delete, update, insert, func, text,
    Column, String, Integer, Float, Date, DateTime, 
    Enum as SqlEnum, Index, ForeignKey, Numeric
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, relationship
from sqlalchemy.exc import SQLAlchemyError
from redis import asyncio as aioredis
import redis.asyncio as redis
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pyzbar import pyzbar
import barcode
from barcode.writer import ImageWriter
import gspread
import requests
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Local Application Imports
from backend.app.database.base import Base
from backend.app.database.database import get_async_db
from backend.app.database.redisclient import (
    get_redis, get_redis_dependency, 
    init_redis, check_redis_connectivity_with_retry, 
    close_redis
)
from backend.app import config
from backend.app.utils.date_utils import UTCDateUtils
from backend.app.utils.field_validators import BaseValidators
from backend.app.utils.barcode_generator import BarcodeGenerator
from backend.app.utils.qr_code_generator import QRCodeGenerator
from backend.app.utils.inventory_updater import InventoryUpdater

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Common Type Hints
RedisClient = aioredis.Redis
DatabaseSession = AsyncSession