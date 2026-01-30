import random
from datetime import date, time, timedelta
from database import SessionLocal, engine, Base
from models.user import User
from models.member import Member
from models.dining_room import DiningRoom
from models.time_slot import TimeSlot
from models.reservation import Reservation
from models.reservation_attendee import ReservationAttendee
from models.rule import Rule
from models.fee import Fee

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
        # 2. INFRASTRUCTURE (Unchanged)
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
        
        slots = [
            TimeSlot(name="Breakfast", start_time=time(8,0), end_time=time(11,0)),
            TimeSlot(name="Lunch", start_time=time(12,0), end_time=time(15,0)),
            TimeSlot(name="Dinner", start_time=time(18,0), end_time=time(21,0)),
            TimeSlot(name="Late Night", start_time=time(21,0), end_time=time(23,30))
        ]
        db.add_all(slots)

        rules = [
            Rule(code="no_call_no_show", name="No Call No Show Fee", base_amount=40.0, fee_type="flat", enabled=True),
            Rule(code="peak_hours", name="Peak Hours Surcharge", base_amount=15.0, fee_type="flat", enabled=True),
            Rule(code="large_party", name="Large Party Fee", base_amount=10.0, threshold=6, fee_type="per_person", enabled=True),
            Rule(code="cancellation", name="Late Cancellation Fee", base_amount=50.0, fee_type="percentage", enabled=True),
        ]
        db.add_all(rules)
        db.flush()

        # ============================================================
        # 3. RANDOMIZED RESERVATIONS + FEES (20 Total)
        # ============================================================
        print("📅 Generating 20 randomized reservations...")
        for _ in range(20):
            creator = random.choice(all_users)
            res_date = date.today() + timedelta(days=random.randint(1, 30))
            
            res = Reservation(
                created_by_id=creator.id,
                dining_room_id=random.choice(rooms).id,
                time_slot_id=random.choice(slots).id,
                date=res_date,
                notes=random.choice(REAL_NOTES),
                status="confirmed"
            )
            db.add(res)
            db.flush()

            # Add attendees
            party_count = 0
            creator_members = [m for m in all_members if m.user_id == creator.id]
            for m in creator_members:
                if random.random() > 0.2: 
                    db.add(ReservationAttendee(
                        reservation_id=res.id, member_id=m.id, name=m.name,
                        attendee_type="member", dietary_restrictions=m.dietary_restrictions
                    ))
                    party_count += 1

            # Add randomized guests
            for _ in range(random.randint(0, 4)):
                db.add(ReservationAttendee(
                    reservation_id=res.id, member_id=None, name=random.choice(REAL_GUESTS),
                    attendee_type="guest", dietary_restrictions=None
                ))
                party_count += 1

            # APPLY FEES BASED ON LOGIC (With Pylance null-checks)
            # 1. Peak Surcharge (Friday or Saturday)
            if res_date.weekday() in [4, 5]:
                peak_rule = db.query(Rule).filter_by(code="peak_hours").first()
                if peak_rule:
                    db.add(Fee(
                        reservation_id=res.id, 
                        rule_id=peak_rule.id, 
                        calculated_amount=peak_rule.base_amount, 
                        paid=False
                    ))

            # 2. Large Party Fee (>= 6 attendees)
            if party_count >= 6:
                lp_rule = db.query(Rule).filter_by(code="large_party").first()
                if lp_rule:
                    db.add(Fee(
                        reservation_id=res.id, 
                        rule_id=lp_rule.id, 
                        quantity=party_count, 
                        calculated_amount=lp_rule.base_amount * party_count, 
                        paid=False
                    ))

        db.commit()
        print("\n🎉 Database seeded successfully with meaningful data and fees!")

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