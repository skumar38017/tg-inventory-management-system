# backend/app/api_gateways.py
from backend.app.utils.common_imports import *

from backend.app.routers import (
    assign_inventory_routes,
    entry_inventory_routes,
    wastage_inventory_routes,
    to_event_routes,
    from_event_router,

)
from  backend.app.barcode_route import qr_code
from backend.app.barcode_route import barcode, list_barcode_qr_code

class APIGateway:
    """Centralized API Gateway for managing all routes and endpoints"""
    
    def __init__(self):
        self.router = APIRouter()
        self._routes_initialized = False
        self._route_prefix = "/api/v1"
        self._registered_routers = []  # Stores tuples of (router, kwargs)
        
    def initialize_routes(self) -> None:
        """Initialize all application routes"""
        if self._routes_initialized:
            return
            
        # Register all route modules
        self.register_router(entry_inventory_routes.router, tags=["Entry Inventory"])
        self.register_router(to_event_routes.router, tags=["To Event Inventory"])
        self.register_router(from_event_router.router, tags=["From Event Inventory"])
        self.register_router(assign_inventory_routes.router, tags=["Assign Inventory"])
        self.register_router(wastage_inventory_routes.router, tags=["Wastage Inventory"])
        self.register_router(qr_code.router, tags=["QR Code"])
        self.register_router(barcode.router, tags=["Barcode"])
        self.register_router(list_barcode_qr_code.router, tags=["List Barcode QR Codes"])
        
        self._routes_initialized = True
    
    def register_router(self, router: APIRouter, **kwargs: Any) -> None:
        """Register a router with the API gateway"""
        self.router.include_router(router, prefix=self._route_prefix, **kwargs)
        self._registered_routers.append((router, kwargs))
    
    def get_all_routes(self) -> List[Dict[str, Any]]:
        """Get metadata about all registered routes"""
        routes = []
        for route in self.router.routes:
            if isinstance(route, APIRoute):
                routes.append({
                    "path": route.path,
                    "name": route.name,
                    "methods": list(route.methods),
                    "tags": route.tags or []
                })
        return routes
    
    def get_router_summary(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get summary of all registered routers"""
        return {
            "routers": [
                {
                    "name": router.__class__.__name__,
                    "prefix": self._route_prefix,
                    "tags": kwargs.get("tags", [])
                }
                for router, kwargs in self._registered_routers
            ]
        }
    
    def mount_to_app(self, app: FastAPI) -> None:
        """Mount all routes to the FastAPI application"""
        app.include_router(self.router)

    @property
    def route_prefix(self) -> str:
        """Get the current route prefix"""
        return self._route_prefix
    
    @route_prefix.setter
    def route_prefix(self, prefix: str) -> None:
        """Set a new route prefix (will require reinitialization)"""
        self._route_prefix = prefix
        self._routes_initialized = False


# Singleton instance of the API Gateway
api_gateway = APIGateway()

def initialize_api_gateway(app: FastAPI) -> None:
    """Initialize and mount all routes to the FastAPI app"""
    api_gateway.initialize_routes()
    api_gateway.mount_to_app(app)