# migrations/set_admin_user.py
#!/usr/bin/env python3
"""
Migration-like script: Set Josh as admin, all others as regular users.

- Safe to run repeatedly (idempotent).
- Use for local/dev. For prod, prefer a proper admin UI or an Alembic migration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.user import User


ADMIN_EMAIL = "josh@josh.com"


def upgrade():
    db = SessionLocal()
    try:
        josh = db.query(User).filter_by(email=ADMIN_EMAIL).first()
        if not josh:
            print(f"❌ Admin user {ADMIN_EMAIL} not found")
            return

        # Set Josh admin
        josh.is_admin = True
        print(f"✅ Set {josh.name} as admin")

        # Set everyone else non-admin
        others = db.query(User).filter(User.email != ADMIN_EMAIL).all()
        for u in others:
            u.is_admin = False

        db.commit()
        print("✅ Permissions updated")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def downgrade():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for u in users:
            u.is_admin = False
        db.commit()
        print("✅ All users set to non-admin")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upgrade()
