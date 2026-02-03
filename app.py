# app.py
import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from database import engine, Base

# Import Routers
from routes.users import router as user_router
from routes.members import router as members_router
from routes.dining_rooms import router as dining_rooms_router
from routes.time_slots import router as time_slots_router
from routes.reservations import router as reservations_router
from routes.reservation_attendees import router as reservation_attendees_router
from routes.rules import router as rules_router
from routes.fees import router as fees_router
from routes.admin import router as admin_router
from routes.reports import router as reports_router

# --- ENVIRONMENT VALIDATION ---
REQUIRED_ENV_VARS = ["DATABASE_URL"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise EnvironmentError(f"❌ Missing required environment variable: {var}")

# --- STARTUP/SHUTDOWN LIFECYCLE ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    env = os.getenv("ENVIRONMENT", "development")
    print(f"🚀 Starting Sterling Catering API v1.0.0")
    print(f"📍 Environment: {env}")
    print(f"🗄️  Database: Connected")
    print(f"🌐 CORS: Configured for {env}")
    
    # Create Tables
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database tables verified")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Sterling Catering API")

# --- FASTAPI APP INITIALIZATION ---
app = FastAPI(
    title="Sterling Catering API",
    description="Premium catering booking system with dynamic fee management",
    version="1.0.0",
    lifespan=lifespan
)

# --- MIDDLEWARE CONFIGURATION ---
# Trust Proxy Headers (Required for HTTPS on Railway/Netlify)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Dynamic CORS Origins based on environment
def get_cors_origins():
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ["https://sterling-client-demo.netlify.app"]
    else:
        return [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:8080",
            "http://localhost:8081",
        ]

origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*--sterling-client-demo\.netlify\.app",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- EXCEPTION HANDLERS (ENSURES CORS ON ERRORS) ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper CORS headers"""
    origin = request.headers.get("origin", "*")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler with CORS headers and detailed logging"""
    import traceback
    
    # Log full error details
    error_id = datetime.utcnow().isoformat()
    print(f"❌ [{error_id}] Unhandled Exception:")
    print(f"   Path: {request.method} {request.url.path}")
    print(f"   Error: {exc}")
    print(traceback.format_exc())
    
    origin = request.headers.get("origin", "*")
    
    # Return sanitized error to client
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": error_id,
            "message": str(exc) if os.getenv("ENVIRONMENT") != "production" else "An error occurred"
        },
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# --- REGISTER ROUTES ---
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(members_router, prefix="/members", tags=["Members"])
app.include_router(dining_rooms_router, prefix="/dining-rooms", tags=["Dining Rooms"])
app.include_router(time_slots_router, prefix="/time-slots", tags=["Time Slots"])
app.include_router(reservations_router, prefix="/reservations", tags=["Reservations"])
app.include_router(reservation_attendees_router, prefix="/reservations", tags=["Reservation Attendees"])
app.include_router(rules_router, prefix="/rules", tags=["Rules"])
app.include_router(fees_router, prefix="/reservations", tags=["Fees"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(reports_router, prefix="/admin/reports", tags=["Reports"])

# --- HEALTH CHECK ---
@app.get("/health", tags=["Health Check"])
def health_check():
    """Detailed health check for monitoring"""
    from database import SessionLocal
    from sqlalchemy import text
    
    # Test database connection
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# --- LOCAL DEVELOPMENT SERVER ---
if __name__ == "__main__":
    import uvicorn
    
    # Railway uses PORT env var, fallback to 8080 for local dev
    port = int(os.getenv("PORT", 8080))
    
    # Disable reload in production for stability
    reload = os.getenv("ENVIRONMENT") != "production"
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=reload
    )