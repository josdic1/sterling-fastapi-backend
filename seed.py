from datetime import time
from database import SessionLocal
from models.user import User
from models.dining_room import DiningRoom
from models.rule import Rule
from models.time_slot import TimeSlot

def seed_database():
    db = SessionLocal()

    try:
        print("🌱 Seeding database (SAFE MODE)...")

        # USERS
        if not db.query(User).first():
            print("👤 Seeding users...")
            users = [
                ("josh@josh.com", "Josh Dicker"),
                ("zach@zach.com", "Zach Scott"),
                ("gabe@gbae.com", "Gabe Scott"),
                ("ariel@ariel.com", "Ariel Scott-Dicker"),
                ("sarah@sarah.com", "Sara Scott"),
                ("jaime@jaime.com", "Jaime Aker"),
                ("brian@brian.com", "Brian Kaiser"),
                ("brandon@brandon.com", "Brandon Kaiser"),
            ]

            for email, name in users:
                user = User(email=email, name=name, is_admin=False)
                user.set_password("1111")
                db.add(user)

        # DINING ROOMS
        if not db.query(DiningRoom).first():
            print("🏛️ Seeding dining rooms...")
            db.add_all([
                DiningRoom(name="Main Hall", capacity=100),
                DiningRoom(name="Garden Room", capacity=50),
                DiningRoom(name="Private Dining", capacity=20),
                DiningRoom(name="Terrace", capacity=30),
                DiningRoom(name="Wine Cellar", capacity=15),
            ])

        # RULES / FEES
        if not db.query(Rule).first():
            print("📜 Seeding rules...")
            db.add_all([
                Rule(code="no_call_no_show", name="No Call No Show Fee", base_amount=40, fee_type="flat", enabled=True),
                Rule(code="peak_hours", name="Peak Hours Surcharge", base_amount=15, fee_type="flat", enabled=True),
                Rule(code="excess_member_guests", name="Excess Guest Fee", base_amount=15, fee_type="per_person", enabled=True),
                Rule(code="excess_occupancy", name="Occupancy Overage Fee", base_amount=15, threshold=12, fee_type="per_person", enabled=True),
                Rule(code="cancellation", name="Late Cancellation Fee", base_amount=50, fee_type="percentage", enabled=True),
            ])

        # TIME SLOTS
        if not db.query(TimeSlot).first():
            print("🕒 Seeding time slots...")
            db.add_all([
                TimeSlot(name="Lunch Early", start_time=time(11, 0), end_time=time(13, 0)),
                TimeSlot(name="Lunch Late", start_time=time(12, 0), end_time=time(14, 0)),
                TimeSlot(name="Dinner Early", start_time=time(17, 0), end_time=time(19, 0)),
                TimeSlot(name="Dinner Peak", start_time=time(18, 0), end_time=time(20, 0)),
                TimeSlot(name="Dinner Late", start_time=time(19, 0), end_time=time(21, 0)),
            ])

        db.commit()
        print("✅ Seeding complete")

    except Exception as e:
        db.rollback()
        print("❌ Seed failed:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
