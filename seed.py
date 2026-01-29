# seed.py
"""
Seed script to populate database with test data.
Run this to reset your database with fresh test data.
"""
from datetime import time  
from database import SessionLocal, engine, Base
from models.user import User
from models.member import Member
from models.dining_room import DiningRoom
from models.time_slot import TimeSlot
from datetime import date
from models.reservation import Reservation
from models.reservation_attendee import ReservationAttendee
from models.rule import Rule
from models.fee import Fee


def seed_database():
    """
    Drop all tables, recreate them, and add seed data.
    WARNING: This deletes ALL data!
    """
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("🔨 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("🌱 Seeding data...")
    
    db = SessionLocal()
    
    try:
        # ============================================================
        # USER 1: Josh
        # ============================================================
        josh_user = User(
            email="josh@josh.com",
            name="Josh",
            is_admin=False
        )
        josh_user.set_password("1111")
        db.add(josh_user)
        db.commit()
        db.refresh(josh_user)
        print(f"✅ Created user: {josh_user.email}")
        
        # Member: Josh (self)
        josh_member = Member(
            user_id=josh_user.id,
            name="Josh",
            relation="self",
            dietary_restrictions="no shellfish"
        )
        db.add(josh_member)
        print(f"   └─ Member: {josh_member.name} ({josh_member.relation})")
        
        # Member: Dorrie (spouse)
        dorrie_member = Member(
            user_id=josh_user.id,
            name="Dorrie",
            relation="spouse",
            dietary_restrictions="no bluecheese"
        )
        db.add(dorrie_member)
        print(f"   └─ Member: {dorrie_member.name} ({dorrie_member.relation})")
        
        
        # ============================================================
        # USER 2: Sarah
        # ============================================================
        sarah_user = User(
            email="sarah@sarah.com",
            name="Sarah",
            is_admin=False
        )
        sarah_user.set_password("1111")
        db.add(sarah_user)
        db.commit()
        db.refresh(sarah_user)
        print(f"✅ Created user: {sarah_user.email}")
        
        # Member: Sarah (self)
        sarah_member = Member(
            user_id=sarah_user.id,
            name="Sarah",
            relation="self",
            dietary_restrictions="no bananas"
        )
        db.add(sarah_member)
        print(f"   └─ Member: {sarah_member.name} ({sarah_member.relation})")
        
        # Member: Reed (spouse/partner)
        reed_member = Member(
            user_id=sarah_user.id,
            name="Reed",
            relation="spouse",
            dietary_restrictions=None
        )
        db.add(reed_member)
        print(f"   └─ Member: {reed_member.name} ({reed_member.relation})")
        
        db.commit()
        
        # ============================================================
        # DINING ROOMS (Infrastructure)
        # ============================================================
        print("\n🏛️  Creating dining rooms...")
        
        dining_rooms = [
            {"name": "Main Hall", "capacity": 100},
            {"name": "Garden Room", "capacity": 50},
            {"name": "Private Dining", "capacity": 20},
            {"name": "Terrace", "capacity": 30},
            {"name": "Wine Cellar", "capacity": 15},
        ]
        
        for room_data in dining_rooms:
            room = DiningRoom(
                name=room_data["name"],
                capacity=room_data["capacity"]
            )
            db.add(room)
            print(f"   └─ {room.name} (capacity: {room.capacity})")
        
        db.commit()

        # ============================================================
        # TIME SLOTS (Infrastructure)
        # ============================================================
        print("\n🕐 Creating time slots...")
        
        time_slots = [
            {"name": "Breakfast", "start_time": time(8, 0), "end_time": time(11, 0)},
            {"name": "Lunch", "start_time": time(12, 0), "end_time": time(15, 0)},
            {"name": "Dinner", "start_time": time(18, 0), "end_time": time(21, 0)},
            {"name": "Late Night", "start_time": time(21, 0), "end_time": time(23, 30)},
        ]
        
        for slot_data in time_slots:
            slot = TimeSlot(
                name=slot_data["name"],
                start_time=slot_data["start_time"],
                end_time=slot_data["end_time"]
            )
            db.add(slot)
            print(f"   └─ {slot.name} ({slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')})")
        
        db.commit()

        # ============================================================
        # SAMPLE RESERVATIONS
        # ============================================================
        print("\n📅 Creating sample reservations...")
        
        # Josh books Main Hall for Dinner on Feb 15
        josh_reservation = Reservation(
            created_by_id=josh_user.id,
            dining_room_id=1,  # Main Hall
            time_slot_id=3,    # Dinner
            date=date(2026, 2, 15),
            notes="Anniversary dinner",
            status="confirmed"
        )
        db.add(josh_reservation)
        print(f"   └─ Josh: Main Hall, Dinner, Feb 15")
        
        # Sarah books Garden Room for Lunch on Feb 20
        sarah_reservation = Reservation(
            created_by_id=sarah_user.id,
            dining_room_id=2,  # Garden Room
            time_slot_id=2,    # Lunch
            date=date(2026, 2, 20),
            notes="Birthday lunch",
            status="confirmed"
        )
        db.add(sarah_reservation)
        print(f"   └─ Sarah: Garden Room, Lunch, Feb 20")
        
        db.commit()

        # ============================================================
        # SAMPLE ATTENDEES
        # ============================================================
        print("\n👥 Adding attendees to reservations...")
        
        # Josh's reservation: Josh + Dorrie + 1 guest
        josh_attendee = ReservationAttendee(
            reservation_id=josh_reservation.id,
            member_id=josh_member.id,
            name=josh_member.name,
            attendee_type="member",
            dietary_restrictions=josh_member.dietary_restrictions
        )
        db.add(josh_attendee)
        
        dorrie_attendee = ReservationAttendee(
            reservation_id=josh_reservation.id,
            member_id=dorrie_member.id,
            name=dorrie_member.name,
            attendee_type="member",
            dietary_restrictions=dorrie_member.dietary_restrictions
        )
        db.add(dorrie_attendee)
        
        guest_attendee = ReservationAttendee(
            reservation_id=josh_reservation.id,
            member_id=None,
            name="Uncle Bob",
            attendee_type="guest",
            dietary_restrictions=None
        )
        db.add(guest_attendee)
        print(f"   └─ Josh's reservation: Josh, Dorrie, Uncle Bob (3 attendees)")
        
        # Sarah's reservation: Sarah + Reed
        sarah_attendee_self = ReservationAttendee(
            reservation_id=sarah_reservation.id,
            member_id=sarah_member.id,
            name=sarah_member.name,
            attendee_type="member",
            dietary_restrictions=sarah_member.dietary_restrictions
        )
        db.add(sarah_attendee_self)
        
        reed_attendee = ReservationAttendee(
            reservation_id=sarah_reservation.id,
            member_id=reed_member.id,
            name=reed_member.name,
            attendee_type="member",
            dietary_restrictions=reed_member.dietary_restrictions
        )
        db.add(reed_attendee)
        print(f"   └─ Sarah's reservation: Sarah, Reed (2 attendees)")
        
        db.commit()

        # ============================================================
        # FEE RULES (Infrastructure)
        # ============================================================
        print("\n💰 Creating fee rules...")
        
        rules_data = [
            {
                "code": "no_call_no_show",
                "name": "No Call No Show Fee",
                "description": "Applied when customer doesn't show up or cancel",
                "fee_type": "flat",
                "base_amount": 40.0,
                "threshold": None,
                "enabled": True
            },
            {
                "code": "peak_hours",
                "name": "Peak Hours Surcharge",
                "description": "Additional fee for Friday/Saturday dinner",
                "fee_type": "flat",
                "base_amount": 15.0,
                "threshold": None,
                "enabled": True
            },
            {
                "code": "large_party",
                "name": "Large Party Fee",
                "description": "Applied for parties of 6 or more",
                "fee_type": "per_person",
                "base_amount": 10.0,
                "threshold": 6,
                "enabled": True
            },
            {
                "code": "cancellation",
                "name": "Late Cancellation Fee",
                "description": "Cancellation within 24 hours",
                "fee_type": "percentage",
                "base_amount": 50.0,  # 50%
                "threshold": None,
                "enabled": True
            },
        ]
        
        for rule_data in rules_data:
            rule = Rule(**rule_data)
            db.add(rule)
            print(f"   └─ {rule.name} (${rule.base_amount})")
        
        db.commit()

        # ============================================================
        # SAMPLE FEES
        # ============================================================
        print("\n💵 Applying sample fees...")
        
        # Apply peak hours fee to Josh's dinner reservation
        peak_hours_rule = db.query(Rule).filter(Rule.code == "peak_hours").first()
        josh_peak_fee = Fee(
            reservation_id=josh_reservation.id,
            rule_id=peak_hours_rule.id, # type: ignore
            quantity=None,
            calculated_amount=15.0,
            paid=False
        )
        db.add(josh_peak_fee)
        print(f"   └─ Applied ${peak_hours_rule.base_amount} peak hours fee to Josh's reservation") # type: ignore
        
        # Apply large party fee to Josh's reservation (3 attendees, so actually doesn't meet threshold)
        # But let's apply it as an example
        large_party_rule = db.query(Rule).filter(Rule.code == "large_party").first()
        josh_party_fee = Fee(
            reservation_id=josh_reservation.id,
            rule_id=large_party_rule.id, # type: ignore
            quantity=3,  # 3 attendees
            calculated_amount=30.0,  # $10 x 3
            paid=False
        )
        db.add(josh_party_fee)
        print(f"   └─ Applied ${30.0} large party fee to Josh's reservation")
        
        db.commit()
        
        
        # ============================================================
        # SUCCESS MESSAGE (moved to end)
        # ============================================================
        print("\n" + "="*50)
        print("🎉 Database seeded successfully!")
        print("="*50)
        print("\n📧 Login credentials:")
        print("   Josh:  josh@josh.com / 1111")
        print("   Sarah: sarah@sarah.com / 1111")
        print("\n")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Confirm before destroying data
    response = input("⚠️  This will DELETE all data. Continue? (yes/no): ")
    if response.lower() == "yes":
        seed_database()
    else:
        print("❌ Seed cancelled.")