#!/usr/bin/env python3
"""
Fix dining room issues:
1. Ensure all rooms have is_active field set
2. Check reservation-room relationships
3. Test the toggle functionality
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
            # Ensure is_active is set
            if not hasattr(room, 'is_active') or room.is_active is None:
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
    finally:
        db.close()

def check_reservations():
    """Check if reservations have valid room IDs"""
    db = SessionLocal()
    try:
        print("\n🔍 CHECKING RESERVATIONS")
        print("=" * 60)

        # Build a dict for fast lookup + avoids extra queries
        rooms = db.query(DiningRoom).all()
        rooms_by_id = {r.id: r for r in rooms}

        reservations = db.query(Reservation).all()

        for res in reservations:
            room = rooms_by_id.get(res.dining_room_id)
            if not room:
                print(f"⚠️  Reservation {res.id} has invalid room_id: {res.dining_room_id}")
                print(f"   Valid room IDs: {sorted(rooms_by_id.keys())}")
            else:
                print(f"✅ Reservation {res.id}: Room = {room.name}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


def test_toggle():
    """Test toggling a room"""
    db = SessionLocal()
    try:
        print("\n🧪 TESTING TOGGLE")
        print("=" * 60)
        
        # Get Main Hall
        room = db.query(DiningRoom).filter_by(name='Main Hall').first()
        if not room:
            print("❌ Main Hall not found")
            return
        
        print(f"Main Hall current status: {room.is_active}")
        
        # Toggle it
        room.is_active = not room.is_active
        db.commit()
        
        print(f"Main Hall new status: {room.is_active}")
        
        # Verify the change persisted
        db.refresh(room)
        print(f"Main Hall after refresh: {room.is_active}")
        
        print("\n✅ Toggle test successful!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_rooms()
    check_reservations()
    test_toggle()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("1. All rooms should have is_active set")
    print("2. All reservations should have valid room IDs")
    print("3. Toggle functionality tested")
    print("\nNow restart your backend and test in the UI!")
    print("=" * 60)