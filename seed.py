import bcrypt
from datetime import time
from database import SessionLocal, engine, Base
from models.user import User
from models.dining_room import DiningRoom
from models.rule import Rule
from models.time_slot import TimeSlot

def seed_database():
    """
    Full infrastructure seed: Users, Rooms, Rules (Fees), and Time Slots.
    Matches your specific SQLAlchemy models.
    """
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("🔨 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. CORE USERS
        # ============================================================
        print("🌱 Seeding Users...")
        users_to_create = [
            {"email": "josh@josh.com", "name": "Josh Dicker"},
            {"email": "zach@zach.com", "name": "Zach Scott"},
            {"email": "gabe@gbae.com", "name": "Gabe Scott"},
            {"email": "ariel@ariel.com", "name": "Ariel Scott-Dicker"},
            {"email": "sarah@sarah.com", "name": "Sara Scott"},
            {"email": "jaime@jaime.com", "name": "Jaime Aker"},
            {"email": "brian@brian.com", "name": "Brian Kaiser"},
            {"email": "brandon@brandon.com", "name": "Brandon Kaiser"}
        ]
        for u_info in users_to_create:
            user = User(email=u_info["email"], name=u_info["name"], is_admin=False)
            user.set_password("1111")
            db.add(user)
        
        # 2. DINING ROOMS
        # ============================================================
        print("🏛️  Creating Dining Rooms...")
        db.add_all([
            DiningRoom(name="Main Hall", capacity=100),
            DiningRoom(name="Garden Room", capacity=50),
            DiningRoom(name="Private Dining", capacity=20),
            DiningRoom(name="Terrace", capacity=30),
            DiningRoom(name="Wine Cellar", capacity=15)
        ])
        
        # 3. RULES (This is what populates your 'Fees' logic)
        # ============================================================
        print("📜 Creating Rules (Fees)...")
        db.add_all([
            Rule(code="no_call_no_show", name="No Call No Show Fee", base_amount=40.0, fee_type="flat", enabled=True),
            Rule(code="peak_hours", name="Peak Hours Surcharge", base_amount=15.0, fee_type="flat", enabled=True),
            Rule(code="excess_member_guests", name="Excess Guest Fee", description="$15 per guest beyond allowance", base_amount=15.0, fee_type="per_person", enabled=True),
            Rule(code="excess_occupancy", name="Occupancy Overage Fee", description="$15 per guest when party > 12", base_amount=15.0, threshold=12, fee_type="per_person", enabled=True),
            Rule(code="cancellation", name="Late Cancellation Fee", base_amount=50.0, fee_type="percentage", enabled=True),
        ])

        # 4. TIME SLOTS (Fixed: using 'name' to match your model)
        # ============================================================
        print("🕒 Creating Time Slots...")
        db.add_all([
            TimeSlot(name="Lunch Early", start_time=time(11, 0), end_time=time(13, 0)),
            TimeSlot(name="Lunch Late", start_time=time(12, 0), end_time=time(14, 0)),
            TimeSlot(name="Dinner Early", start_time=time(17, 0), end_time=time(19, 0)),
            TimeSlot(name="Dinner Peak", start_time=time(18, 0), end_time=time(20, 0)),
            TimeSlot(name="Dinner Late", start_time=time(19, 0), end_time=time(21, 0))
        ])
        
        db.commit()
        print("\n🎉 Database FULLY seeded!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()