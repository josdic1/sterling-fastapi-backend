import random
from datetime import date, time, timedelta
from database import SessionLocal, engine, Base
from models.user import User
from models.member import Member
from models.dining_room import DiningRoom
from models.rule import Rule

def seed_database():
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("🔨 Creating all tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("🌱 Seeding Users...")

        # Add is_admin per user (at least one admin)
        users_data = [
            {"email": "josh@josh.com", "name": "Josh Dicker", "is_admin": True},
            {"email": "zach@zach.com", "name": "Zach Scott", "is_admin": False},
            {"email": "gabe@gabe.com", "name": "Gabe Scott", "is_admin": False},
            {"email": "ariel@ariel.com", "name": "Ariel Scott-Dicker", "is_admin": False},
            {"email": "sarah@sarah.com", "name": "Sarah Scott", "is_admin": False},
            {"email": "jaime@jaime.com", "name": "Jaime Aker", "is_admin": False},
            {"email": "brian@brian.com", "name": "Brian Kaiser", "is_admin": False},
            {"email": "brandon@brandon.com", "name": "Brandon Kaiser", "is_admin": False},
        ]

        for u in users_data:
            user = User(
                email=u["email"],
                name=u["name"],
                is_admin=bool(u["is_admin"]),
            )
            user.set_password("1111")
            db.add(user)

        print("🏛️  Creating Dining Rooms...")
        rooms = [
            DiningRoom(name="Main Hall", capacity=100),
            DiningRoom(name="Garden Room", capacity=50),
            DiningRoom(name="Private Dining", capacity=20),
            DiningRoom(name="Terrace", capacity=30),
            DiningRoom(name="Wine Cellar", capacity=15),
        ]
        db.add_all(rooms)

        print("📜 Creating Fee Rules...")
        rules = [
            Rule(
                code="no_call_no_show",
                name="No Call No Show Fee",
                base_amount=40.0,
                fee_type="flat",
                enabled=1,
            ),
            Rule(
                code="peak_hours",
                name="Peak Hours Surcharge",
                base_amount=15.0,
                fee_type="flat",
                enabled=1,
            ),
            Rule(
                code="excess_member_guests",
                name="Excess Guest Fee",
                description="$15 per guest beyond member allowance (4 guests per member)",
                base_amount=15.0,
                fee_type="per_person",
                enabled=1,
            ),
            Rule(
                code="excess_occupancy",
                name="Occupancy Overage Fee",
                description="$15 per guest when total party exceeds 12 people",
                base_amount=15.0,
                threshold=12,
                fee_type="per_person",
                enabled=1,
            ),
            Rule(
                code="cancellation",
                name="Late Cancellation Fee",
                base_amount=50.0,
                fee_type="percentage",
                enabled=1,
            ),
        ]
        db.add_all(rules)

        db.commit()

        admins = [u for u in users_data if u.get("is_admin")]
        print("\n🎉 Database seeded successfully!")
        print("\n📋 Summary:")
        print(f"  - {len(users_data)} users created (password: 1111)")
        print(f"  - {len(admins)} admins: {', '.join(a['email'] for a in admins)}")
        print(f"  - {len(rooms)} dining rooms created")
        print(f"  - {len(rules)} fee rules created")
        print("\n✅ Ready for you to add members, reservations, and attendees!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    response = input("⚠️  This will DELETE all data. Continue? (yes/no): ")
    if response.lower() == "yes":
        seed_database()
    else:
        print("❌ Seed cancelled.")
