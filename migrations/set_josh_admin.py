#!/usr/bin/env python3
"""
Migration: Set Josh as admin, all others as regular users
Run this once to update user permissions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.user import User

def upgrade():
    """Set Josh as admin, everyone else as regular user"""
    db = SessionLocal()
    try:
        # Set Josh as admin
        josh = db.query(User).filter_by(email='josh@josh.com').first()
        if josh:
            josh.is_admin = True
            print(f"✅ Set {josh.name} as admin")
        else:
            print("❌ Josh not found - run seed.py first")
            return
        
        # Set all others as non-admin
        other_users = db.query(User).filter(User.email != 'josh@josh.com').all()
        for user in other_users:
            user.is_admin = False
            print(f"✅ Set {user.name} as regular user")
        
        db.commit()
        print("\n🎉 Migration complete!")
        print(f"   Admin: {josh.name} ({josh.email})")
        print(f"   Regular users: {len(other_users)}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

def downgrade():
    """Revert all users to non-admin"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            user.is_admin = False
        db.commit()
        print("✅ All users set to non-admin")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Setting user permissions...")
    upgrade()