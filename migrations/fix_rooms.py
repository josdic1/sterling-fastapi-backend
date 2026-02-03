# migrations/add_new_fee_rules.py
#!/usr/bin/env python3
"""
Migration: Ensure new fee rules exist (idempotent)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.rule import Rule


def upgrade():
    db = SessionLocal()
    try:
        # Check for excess_member_guests rule
        excess_guests = db.query(Rule).filter_by(code="excess_member_guests").first()
        if not excess_guests:
            db.add(Rule(
                code="excess_member_guests",
                name="Excess Guest Fee",
                description="$15 per guest beyond member allowance (4 guests per member)",
                base_amount=15.0,
                fee_type="per_person",
                threshold=None,
                enabled=True
            ))
            print("✅ Added excess_member_guests rule")
        else:
            print("ℹ️  excess_member_guests already exists")
            # Update to ensure correct values
            excess_guests.base_amount = 15.0
            excess_guests.fee_type = "per_person"
            excess_guests.threshold = None
            excess_guests.enabled = True
            print("✅ Updated excess_member_guests rule")

        # Check for excess_occupancy rule
        excess_occupancy = db.query(Rule).filter_by(code="excess_occupancy").first()
        if not excess_occupancy:
            db.add(Rule(
                code="excess_occupancy",
                name="Occupancy Overage Fee",
                description="$15 per guest when total party exceeds 12 people",
                base_amount=15.0,
                fee_type="per_person",
                threshold=12,
                enabled=True
            ))
            print("✅ Added excess_occupancy rule")
        else:
            print("ℹ️  excess_occupancy already exists")
            # Update to ensure correct values
            excess_occupancy.base_amount = 15.0
            excess_occupancy.fee_type = "per_person"
            excess_occupancy.threshold = 12
            excess_occupancy.enabled = True
            print("✅ Updated excess_occupancy rule")

        db.commit()
        print("✅ Fee rules migration complete")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upgrade()