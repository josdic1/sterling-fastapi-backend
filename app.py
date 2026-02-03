# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
from routes.admin import router as admin_router  # NEW: Admin routes
from routes.reports import router as reports_router  # NEW: Reports

# Create Tables (if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sterling Catering API",
    description="Premium catering booking system with dynamic fee management",
    version="1.0.0"
)

# Trust Proxy Headers (Required for HTTPS on Railway/Netlify)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# --- CORS CONFIGURATION ---
# We define specific origins for local dev and production
origins = [
    "http://localhost:8080", # Backend (Swagger)
    "http://localhost:8081", # Alternative Backend
    "http://localhost:5173", # Vite Default
    "http://localhost:5174", # Vite Fallback
    "https://sterling-client-demo.netlify.app", # Production Frontend
]

app.add_middleware(
    CORSMiddleware,
    # Allow Netlify Preview builds (e.g. https://deploy-preview-123--sterling.netlify.app)
    allow_origin_regex=r"https://.*--sterling-client-demo\.netlify\.app",
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(admin_router, prefix="/admin", tags=["Admin"])  # NEW: Admin routes
app.include_router(reports_router, prefix="/admin/reports", tags=["Reports"])  # NEW: Reports

@app.get("/", tags=["Health Check"])
def home():
    return {"message": "Sterling Catering API"}

if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 for Railway/Deployment compatibility
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)