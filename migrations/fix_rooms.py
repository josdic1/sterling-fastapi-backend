# scripts/fix_rooms.py
#!/usr/bin/env python3
"""
Fix dining room issues:
1) Ensure all rooms have is_active set (True if NULL)
2) Check reservation -> room relationships
3) (Optional) Test toggle on a specific room name

NOTE:
- This is a one-off maintenance script, NOT a migration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.dining_room import DiningRoom
from models.reservation import Reservation


def fix_all_rooms():
    """Ensure all rooms have is_active properly set"""
    db = SessionLocal()
    try:
        rooms = db.query(DiningRoom).all()
        print("\n🔧 FIXING ROOM DATA")
        print("=" * 60)

        for room in rooms:
            if room.is_active is None:
                room.is_active = True
                print(f"✅ Set {room.name} to ACTIVE (was None)")
            else:
                status = "ACTIVE" if room.is_active else "INACTIVE"
                print(f"ℹ️  {room.name}: {status}")

        db.commit()
        print("\n✅ All rooms fixed!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def check_reservations():
    """Check if reservations have valid room IDs"""
    db = SessionLocal()
    try:
        print("\n🔍 CHECKING RESERVATIONS")
        print("=" * 60)

        rooms = db.query(DiningRoom).all()
        rooms_by_id = {r.id: r for r in rooms}

        reservations = db.query(Reservation).all()

        for res in reservations:
            room = rooms_by_id.get(res.dining_room_id)
            if not room:
                print(
                    f"⚠️  Reservation {res.id} has invalid room_id: {res.dining_room_id}"
                )
                print(f"   Valid room IDs: {sorted(rooms_by_id.keys())}")
            else:
                print(f"✅ Reservation {res.id}: Room = {room.name}")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def test_toggle(room_name="Main Hall"):
    """Test toggling a room (optional)"""
    db = SessionLocal()
    try:
        print("\n🧪 TESTING TOGGLE")
        print("=" * 60)

        room = db.query(DiningRoom).filter_by(name=room_name).first()
        if not room:
            print(f"❌ {room_name} not found")
            return

        print(f"{room_name} current status: {room.is_active}")

        room.is_active = not room.is_active
        db.commit()

        db.refresh(room)
        print(f"{room_name} after toggle+refresh: {room.is_active}")

        print("\n✅ Toggle test successful!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fix_all_rooms()
    check_reservations()
    # comment this out if you don't want to actually flip a room in prod:
    # test_toggle("Main Hall")

    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("1. All rooms should have is_active set")
    print("2. All reservations should have valid room IDs")
    print("3. Toggle test is optional (commented out by default)")
    print("=" * 60)
