# backend/app/database/database.py

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from backend.app.config import SYNC_DB_URL, ASYNC_DB_URL
from sqlalchemy.exc import SQLAlchemyError
import asyncio
import time
import logging

# Set up logging to display info and error messages
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Sync Database Setup
sync_engine = create_engine(SYNC_DB_URL, future=True, echo=True)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base class for declarative models
Base = declarative_base()

def get_sync_db():
    """Create a new synchronous database session."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async Database Setup
async_engine = create_async_engine(ASYNC_DB_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False
)

async def get_async_db():
    """Create a new asynchronous database session."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()

# Check Sync Database Connectivity
def check_sync_db_connectivity():
    """Check the connectivity to the synchronous database."""
    try:
        logger.info("Checking synchronous database connectivity...")
        with sync_engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.fetchone():
                logger.info("Sync database is connected.")
                return True
    except SQLAlchemyError as e:
        logger.error(f"Sync database connection failed: {e}")
        return False

# Check Async Database Connectivity
async def check_async_db_connectivity():
    """Check the connectivity to the asynchronous database."""
    try:
        logger.info("Checking asynchronous database connectivity...")
        async with async_engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            if result.fetchone():
                logger.info("Async database is connected.")
                return True
    except SQLAlchemyError as e:
        logger.error(f"Async database connection failed: {e}")
        return False

# Run Connectivity Checks (Sync and Async)
def check_db_connectivity():
    """Check both sync and async database connectivity."""
    logger.info("Starting synchronous database connectivity check...")
    if check_sync_db_connectivity():
        logger.info("Sync DB check passed.")
    else:
        logger.error("Sync DB check failed.")
    
    logger.info("Starting asynchronous database connectivity check...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_async_db_connectivity())

# Optional: Retry mechanism for sync database connectivity check
def check_sync_db_connectivity_with_retry(retries=3, delay=5):
    """Check the connectivity to the synchronous database with retries."""
    attempt = 0
    while attempt < retries:
        try:
            logger.info(f"Attempting sync DB connectivity... (Attempt {attempt + 1}/{retries})")
            with sync_engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                if result.fetchone():
                    logger.info("Sync database is connected.")
                    return True
        except SQLAlchemyError as e:
            logger.error(f"Sync database connection failed on attempt {attempt + 1}: {e}")
            attempt += 1
            logger.info(f"Retrying... ({attempt}/{retries})")
            time.sleep(delay)
    logger.error("Sync database connection failed after retries.")
    return False

# Optional: Retry mechanism for async database connectivity check
async def check_async_db_connectivity_with_retry(retries=3, delay=5):
    """Check the connectivity to the asynchronous database with retries."""
    attempt = 0
    while attempt < retries:
        try:
            logger.info(f"Attempting async DB connectivity... (Attempt {attempt + 1}/{retries})")
            async with async_engine.connect() as connection:
                result = await connection.execute(text("SELECT 1"))
                if result.fetchone():
                    logger.info("Async database is connected.")
                    return True
        except SQLAlchemyError as e:
            logger.error(f"Async database connection failed on attempt {attempt + 1}: {e}")
            attempt += 1
            logger.info(f"Retrying in {delay} seconds... ({attempt}/{retries})")
            await asyncio.sleep(delay)
    logger.error("Async database connection failed after retries.")
    return False
