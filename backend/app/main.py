# backend/app/main.py

import asyncio
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from backend.app.database.database import check_db_connectivity, check_sync_db_connectivity_with_retry, check_async_db_connectivity_with_retry
from backend.app.database.redisclient import check_redis_connectivity_with_retry
from fastapi.staticfiles import StaticFiles
from backend.app.routers import assign_inventory_routes, entry_inventory_routes,  wastage_inventory_routes, to_event_routes, from_event_router


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

# Root Endpoint
@app.get("/", include_in_schema=True)
async def index():
    """
    Root endpoint.
    """
    logger.info("Root endpoint accessed.")
    return {"message": "Ticket Management System"}
@app.on_event("startup")
async def startup_event():
    """
    Event handler that runs on application startup.
    - Ensures DB, Redis, and Razorpay connections are established.
    """
    logger.info("Application started.")
    logger.info("Running setup tasks...")

    # Checking Redis connectivity
    logger.info("Checking Redis connectivity...")
    if not check_redis_connectivity_with_retry(retries=3, delay=5):
        logger.error("Redis connectivity check failed during startup.")
        raise HTTPException(status_code=500, detail="Redis connection failed")

    logger.info("Redis connection successful.")

    # Checking database connectivity (sync and async)
    logger.info("Checking database connectivity...")

    # Sync DB Check
    if not check_sync_db_connectivity_with_retry(retries=3, delay=5):
        logger.error("Sync database connectivity check failed during startup.")
        raise HTTPException(status_code=500, detail="Sync database connection failed")

    # Async DB Check
    await check_async_db_connectivity_with_retry(retries=3, delay=5)

    logger.info("Database connection successful.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Event handler that runs when the application shuts down.
    """
    logger.info("Application shutdown...")

# Exception Handler for HTTPException
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    """
    Custom exception handler for HTTP exceptions.
    """
    status_code = 400 if exc.status_code == 422 else exc.status_code
    logger.error(f"HTTPException: {exc.detail} | Path: {request.url.path} | Status Code: {status_code}")

    response_content = {
        "error": "Bad Request" if status_code == 400 else "HTTP Error",
        "detail": exc.detail,
        "path": request.url.path,
    }

    return JSONResponse(status_code=status_code, content=response_content)

# Include the entry inventory routes with a versioned prefix
app.include_router(entry_inventory_routes.router, prefix="/api/v1", tags=["Entry Inventory"])
app.include_router(to_event_routes.router, prefix="/api/v1", tags=["To Event Inventory"])
app.include_router(from_event_router.router, prefix="/api/v1", tags=["From Event Inventory"])
app.include_router(assign_inventory_routes.router, prefix="/api/v1", tags=["Assign Inventory"])
app.include_router(wastage_inventory_routes.router, prefix="/api/v1", tags=["Wastage Inventory"])

if __name__ == "__main__":
    # Running the FastAPI app with Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
