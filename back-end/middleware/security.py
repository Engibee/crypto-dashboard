from fastapi import Request
from fastapi.responses import JSONResponse
from config.settings import ALLOWED_ORIGINS, API_SECRET_KEY

async def block_unauthorized_origins(request: Request, call_next):
    # Only allow health endpoint for monitoring
    if request.url.path in ["/health"]:
        return await call_next(request)
    
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    host = request.headers.get("host")
    user_agent = request.headers.get("user-agent", "")
    
    # Block direct browser access (no origin/referer from address bar)
    if not origin and not referer:
        # Allow if it's a legitimate API client (not a browser)
        if not any(browser in user_agent.lower() for browser in ["mozilla", "chrome", "safari", "edge", "firefox"]):
            return await call_next(request)
        return JSONResponse(status_code=403, content={"detail": "Direct browser access not allowed"})
    
    # Check origin if present
    if origin and not any(origin.startswith(allowed) for allowed in ALLOWED_ORIGINS):
        return JSONResponse(status_code=403, content={"detail": "Origin not allowed"})
    
    # Check referer if present
    if referer and not any(referer.startswith(allowed) for allowed in ALLOWED_ORIGINS):
        return JSONResponse(status_code=403, content={"detail": "Referer not allowed"})
    
    return await call_next(request)