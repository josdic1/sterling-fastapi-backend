# migrations/add_new_fee_rules.py
#!/usr/bin/env python3
"""
Migration: Ensure new fee rules exist (idempotent)

- excess_member_guests
- excess_occupancy
- disable old large_party (if present)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.rule import Rule


def upgrade():
    db = SessionLocal()
    try:
        excess_guests = db.query(Rule).filter_by(code="excess_member_guests").first()
        excess_occupancy = db.query(Rule).filter_by(code="excess_occupancy").first()

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

        old_rule = db.query(Rule).filter_by(code="large_party").first()
        if old_rule and old_rule.enabled:
            old_rule.enabled = False
            print("✅ Disabled old large_party rule")
        elif old_rule:
            print("ℹ️  old large_party rule already disabled")

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
