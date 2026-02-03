# app.py
import os
from datetime import datetime
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import HTTPException
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    from database import engine, Base
except ImportError as e:
    print(f"❌ FATAL: Missing dependency - {e}")
    raise

# Import Routers
try:
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
except ImportError as e:
    print(f"❌ FATAL: Could not import routes - {e}")
    raise

# --- ENVIRONMENT VALIDATION ---
print("\n" + "="*60)
print("🚀 STERLING CATERING API - STARTUP CHECK")
print("="*60)

# Check critical environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if not DATABASE_URL:
    print("❌ FATAL: DATABASE_URL not set!")
    raise EnvironmentError("Missing DATABASE_URL")

if not SECRET_KEY:
    print("⚠️  WARNING: SECRET_KEY not set - using default (INSECURE!)")
else:
    print("✅ SECRET_KEY configured")

print(f"✅ DATABASE_URL configured: {DATABASE_URL[:30]}...")
print(f"✅ ENVIRONMENT: {ENVIRONMENT}")
print("="*60 + "\n")

# --- STARTUP/SHUTDOWN LIFECYCLE ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🚀 Starting Sterling Catering API v1.0.0")
    print(f"📍 Environment: {ENVIRONMENT}")
    
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✅ Database tables verified")
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise
    
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
    if ENVIRONMENT == "production":
        return ["https://sterling-client-demo.netlify.app"]
    else:
        return [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:8080",
            "http://localhost:8081",
        ]

origins = get_cors_origins()

print(f"🌐 CORS configured for: {origins}")

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
    
    print(f"⚠️  HTTP {exc.status_code}: {exc.detail}")
    
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
    print(f"❌ [{error_id}] UNHANDLED EXCEPTION:")
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
            "message": str(exc) if ENVIRONMENT != "production" else "An error occurred"
        },
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# --- REGISTER ROUTES ---
try:
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
    print("✅ All routes registered successfully")
except Exception as e:
    print(f"❌ Route registration error: {e}")
    raise

# --- HEALTH CHECK ---
@app.get("/", tags=["Health Check"])
def home():
    """API health check with diagnostic info"""
    return {
        "message": "Sterling Catering API",
        "version": "1.0.0",
        "status": "operational",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "cors_origins": origins
    }

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
    reload = ENVIRONMENT != "production"
    
    print(f"\n🚀 Starting server on port {port} (reload={reload})")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=reload
    )