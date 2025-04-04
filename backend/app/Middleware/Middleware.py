#  backend/app/Middleware/Middleware.py

# Middleware to detect public scans (add to FastAPI app)
@app.middleware("http")
async def public_scan_detector(request: Request, call_next):
    is_public = 'internal-auth' not in request.headers
    if is_public and '/scan/' in request.url.path:
        request.state.is_public = True
    return await call_next(request)