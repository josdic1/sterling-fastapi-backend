# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes.users import router as user_router
from routes.members import router as members_router
from routes.dining_rooms import router as dining_rooms_router
from routes.time_slots import router as time_slots_router
from routes.reservations import router as reservations_router
from routes.reservation_attendees import router as reservation_attendees_router
from routes.rules import router as rules_router
from routes.fees import router as fees_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sterling Catering API",
    description="Premium catering booking system with dynamic fee management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "https://sterling-react-frontend.vercel.app",  # ADD THIS
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(members_router, prefix="/members", tags=["Members"])
app.include_router(dining_rooms_router, prefix="/dining-rooms", tags=["Dining Rooms"])
app.include_router(time_slots_router, prefix="/time-slots", tags=["Time Slots"])
app.include_router(reservations_router, prefix="/reservations", tags=["Reservations"])
app.include_router(reservation_attendees_router, prefix="/reservations", tags=["Reservation Attendees"])
app.include_router(rules_router, prefix="/rules", tags=["Rules"])
app.include_router(fees_router, prefix="/reservations", tags=["Fees"])

@app.get("/", tags=["Health Check"])
def home():
    return {"message": "Sterling Catering API"}

if __name__ == "__main__":
    import uvicorn
    import os
    # Default to 8080 locally, but use Railway's $PORT if available
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)