# backend/app/main.py
from backend.app.utils.common_imports import *

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
redis_client: aioredis.Redis = Depends(get_redis_dependency)

# Set up logging for the main script
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
# Mount static files directory
# Mount both barcode and qrcode directories
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/public", StaticFiles(directory="backend/app/public"), name="public")
app.mount("/templates", StaticFiles(directory="backend/app/templates"), name="templates")

# Enable CORS for development only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
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
        
        # Initialize rate limiter
        redis_client = await get_redis()
        await FastAPILimiter.init(redis_client)
        logger.info("Rate limiter initialized successfully.")

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
        host = "0.0.0.0" if config.ENVIRONMENT == "production" else "127.0.0.1",
        port=config.PORT,
        reload=True,
        log_level="info"
    )