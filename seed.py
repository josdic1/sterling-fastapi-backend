import random
from datetime import date, time, timedelta
from database import SessionLocal, engine, Base
from models.user import User
from models.member import Member
from models.dining_room import DiningRoom
from models.reservation import Reservation
from models.reservation_attendee import ReservationAttendee
from models.rule import Rule
from models.fee import Fee
from routes.reservations import apply_automatic_fees

# Meaningful data pools for randomized content
REAL_GUESTS = ["Uncle Bob", "Aunt May", "Cousin Vinny", "The Neighbors", "Work Team", "Client Group", "The Johnsons"]
REAL_NOTES = ["Anniversary celebration!", "Needs a high chair", "Window seat if possible", "Quiet corner", "Quick lunch", "Splitting the check"]

def seed_database():
    """
    Drops all tables, recreates them, and populates with specific user/member 
    data and 20 randomized reservations with attendee and fee logic.
    """
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("🔨 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("🌱 Seeding Users and Members...")
        # ============================================================
        # 1. USERS & MEMBERS DATA (Your actual list)
        # ============================================================
        users_data = [
            {"email": "josh@josh.com", "name": "Josh Dicker", "members": [
                {"name": "Josh Dicker", "rel": "self", "diet": "No shellfish, No blue cheese"},
                {"name": "Dorrie Goodman", "rel": "spouse", "diet": "No olives, No blue cheese"},
                {"name": "Demi Dicker", "rel": "daughter", "diet": "No spicy"}
            ]},
            {"email": "zach@zach.com", "name": "Zach Scott", "members": [
                {"name": "Zach Scott", "rel": "self", "diet": "No bananas"},
                {"name": "Cynthia Chen", "rel": "authorized", "diet": None},
                {"name": "Sadie Scott", "rel": "daughter", "diet": "No oysters"},
                {"name": "Tess Scott", "rel": "daughter", "diet": "No pork"}
            ]},
            {"email": "gabe@gbae.com", "name": "Gabe Scott", "members": [
                {"name": "Gabe Scott", "rel": "self", "diet": "No dairy"},
                {"name": "Amanda Siegel", "rel": "authorized", "diet": None},
                {"name": "Palmer Scott", "rel": "daughter", "diet": "No tuna"},
                {"name": "Miller Scott", "rel": "daughter", "diet": None}
            ]},
            {"email": "ariel@ariel.com", "name": "Ariel Scott-Dicker", "members": [
                {"name": "Ariel Scott-Dicker", "rel": "self", "diet": "No sardines"}
            ]},
            {"email": "sarah@sarah.com", "name": "Sara Scott", "members": [
                {"name": "Sarah Scott", "rel": "self", "diet": "No bananas"},
                {"name": "Reed Edwards", "rel": "spouse", "diet": None},
                {"name": "Zoe Scott-Edwards", "rel": "daughter", "diet": "No runny eggs"},
                {"name": "Chase Scott-Edwards", "rel": "son", "diet": None}
            ]},
            {"email": "jaime@jaime.com", "name": "Jaime Aker", "members": [
                {"name": "Jaime Aker", "rel": "self", "diet": "No curry"},
                {"name": "Nat Aker", "rel": "spouse", "diet": "Vegan"},
                {"name": "Nolan Aker", "rel": "son", "diet": "Vegan"}
            ]},
            {"email": "brian@brian.com", "name": "Brian Kaiser", "members": [
                {"name": "Brian Kaiser", "rel": "self", "diet": "No fish"},
                {"name": "Vicki Kaiser", "rel": "spouse", "diet": "No olives, No shellfish"}
            ]},
            {"email": "brandon@brandon.com", "name": "Brandon Kaiser", "members": [
                {"name": "Brandon Kaiser", "rel": "self", "diet": None},
                {"name": "Karolina Kaiser", "rel": "spouse", "diet": "No pears"}
            ]}
        ]

        all_users = []
        all_members = []

        for u_info in users_data:
            user = User(email=u_info["email"], name=u_info["name"], is_admin=False)
            user.set_password("1111")
            db.add(user)
            db.flush() 
            all_users.append(user)
            
            for m_info in u_info["members"]:
                member = Member(
                    user_id=user.id,
                    name=m_info["name"],
                    relation=m_info["rel"],
                    dietary_restrictions=m_info["diet"]
                )
                db.add(member)
                all_members.append(member)
        
        # ============================================================
        # 2. INFRASTRUCTURE
        # ============================================================
        print("🏛️  Creating Infrastructure...")
        rooms = [
            DiningRoom(name="Main Hall", capacity=100),
            DiningRoom(name="Garden Room", capacity=50),
            DiningRoom(name="Private Dining", capacity=20),
            DiningRoom(name="Terrace", capacity=30),
            DiningRoom(name="Wine Cellar", capacity=15)
        ]
        db.add_all(rooms)
        
        rules = [
            Rule(code="no_call_no_show", name="No Call No Show Fee", base_amount=40.0, fee_type="flat", enabled=True),
            Rule(code="peak_hours", name="Peak Hours Surcharge", base_amount=15.0, fee_type="flat", enabled=True),
            Rule(code="excess_member_guests", name="Excess Guest Fee", description="$15 per guest beyond member allowance (4 guests per member)", base_amount=15.0, fee_type="per_person", enabled=True),
            Rule(code="excess_occupancy", name="Occupancy Overage Fee", description="$15 per guest when total party exceeds 12 people", base_amount=15.0, threshold=12, fee_type="per_person", enabled=True),
            Rule(code="cancellation", name="Late Cancellation Fee", base_amount=50.0, fee_type="percentage", enabled=True),
        ]
        
        db.add_all(rules)
        db.flush()

        # ============================================================
        # 3. RANDOMIZED RESERVATIONS + FEES (20 Total)
        # ============================================================
        print("📅 Generating 20 randomized reservations...")
        
        # Time slot options (start_time, end_time)
        lunch_times = [
            (time(11, 0), time(13, 0)),
            (time(11, 15), time(13, 15)),
            (time(11, 30), time(13, 30)),
            (time(11, 45), time(13, 45)),
            (time(12, 0), time(14, 0)),
        ]
        
        dinner_times = [
            (time(16, 0), time(18, 0)),
            (time(16, 30), time(18, 30)),
            (time(17, 0), time(19, 0)),
            (time(17, 30), time(19, 30)),
            (time(18, 0), time(20, 0)),
            (time(18, 30), time(20, 30)),
        ]
        
        for _ in range(20):
            creator = random.choice(all_users)
            res_date = date.today() + timedelta(days=random.randint(1, 60))
            
            # Pick meal type and time slot
            if random.random() < 0.5:
                meal_type = "lunch"
                start_time, end_time = random.choice(lunch_times)
            else:
                meal_type = "dinner"
                start_time, end_time = random.choice(dinner_times)
            
            res = Reservation(
                created_by_id=creator.id,
                dining_room_id=random.choice(rooms).id,
                date=res_date,
                meal_type=meal_type,
                start_time=start_time,
                end_time=end_time,
                notes=random.choice(REAL_NOTES),
                status="confirmed"
            )
            db.add(res)
            db.flush()

            # Add attendees
            creator_members = [m for m in all_members if m.user_id == creator.id]
            for m in creator_members:
                if random.random() > 0.2: 
                    db.add(ReservationAttendee(
                        reservation_id=res.id, 
                        member_id=m.id, 
                        name=m.name,
                        attendee_type="member", 
                        dietary_restrictions=m.dietary_restrictions
                    ))

            # Add randomized guests
            for _ in range(random.randint(0, 6)):
                db.add(ReservationAttendee(
                    reservation_id=res.id, 
                    member_id=None, 
                    name=random.choice(REAL_GUESTS),
                    attendee_type="guest", 
                    dietary_restrictions=None
                ))

            db.flush()  # Make sure attendees are saved
            
            # USE THE AUTOMATIC FEE FUNCTION
            apply_automatic_fees(db, res)

        db.commit()
        print("\n🎉 Database seeded successfully!")

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