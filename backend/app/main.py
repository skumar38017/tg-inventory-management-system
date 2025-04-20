# backend/app/main.py
import asyncio
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database.database import (
    check_db_connectivity, 
    check_sync_db_connectivity_with_retry, 
    check_async_db_connectivity_with_retry
)
from backend.app.database.redisclient import (
    init_redis,
    check_redis_connectivity_with_retry,
    close_redis
)
from backend.app.api_gateways import initialize_api_gateway

# Set up logging for the main script
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# FastAPI App Initialization
app = FastAPI(
    title="Tagglab - Inventory Management System",
    description="This is an inventory management system for the tagglab course.",
    version="1.1.0",
)

# Enable CORS for development only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=True)
async def index():
    """Root endpoint."""
    logger.info("Root endpoint accessed.")
    return {"message": "Ticket Management System"}

@app.get("/api/routes", include_in_schema=True)
async def list_routes():
    """List all available API routes"""
    from backend.app.api_gateways import api_gateway
    return {
        "routes": api_gateway.get_all_routes(),
        "routers": api_gateway.get_router_summary()
    }

@app.on_event("startup")
async def startup_event():
    """Event handler that runs on application startup."""
    logger.info("Application started.")
    logger.info("Running setup tasks...")

    try:
        # Initialize Redis
        await init_redis()
        
        # Checking Redis connectivity with retries
        logger.info("Checking Redis connectivity...")
        if not await check_redis_connectivity_with_retry(retries=3, delay=5):
            raise RuntimeError("Redis connection failed after retries")
        logger.info("Redis connection successful.")

        # Checking database connectivity
        logger.info("Checking database connectivity...")
        
        # Sync DB Check
        if not check_sync_db_connectivity_with_retry(retries=3, delay=5):
            raise RuntimeError("Sync database connection failed")
        
        # Async DB Check
        if not await check_async_db_connectivity_with_retry(retries=3, delay=5):
            raise RuntimeError("Async database connection failed")
            
        logger.info("Database connection successful.")

        # Initialize API Gateway
        initialize_api_gateway(app)
        logger.info("API Gateway initialized successfully.")

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        # Ensure clean shutdown if startup fails
        await shutdown_event()
        raise HTTPException(
            status_code=500,
            detail=f"Application startup failed: {str(e)}"
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Event handler that runs when the application shuts down."""
    logger.info("Application shutdown...")
    try:
        await close_redis()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    """Custom exception handler for HTTP exceptions."""
    status_code = 400 if exc.status_code == 422 else exc.status_code
    logger.error(
        f"HTTPException: {exc.detail} | "
        f"Path: {request.url.path} | "
        f"Status Code: {status_code}"
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Bad Request" if status_code == 400 else "HTTP Error",
            "detail": exc.detail,
            "path": request.url.path,
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )