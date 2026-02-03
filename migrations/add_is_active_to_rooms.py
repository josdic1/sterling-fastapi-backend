#!/usr/bin/env python3
"""
Migration: Add is_active field to dining_rooms table
Allows admin to enable/disable rooms without deleting them
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def upgrade():
    """Add is_active column to dining_rooms"""
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("PRAGMA table_info(dining_rooms)"))
        columns = [row[1] for row in result]
        
        if 'is_active' not in columns:
            # Add column with default true
            conn.execute(text("""
                ALTER TABLE dining_rooms 
                ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL
            """))
            print("✅ Added is_active column to dining_rooms")
        else:
            print("ℹ️  is_active column already exists")
        
        # Set all existing rooms to active
        conn.execute(text("""
            UPDATE dining_rooms 
            SET is_active = 1 
            WHERE is_active IS NULL
        """))
        
        conn.commit()
    
    print("✅ Migration complete")

def downgrade():
    """Remove is_active column"""
    with engine.connect() as conn:
        # SQLite doesn't support DROP COLUMN easily
        # Would need to recreate table
        print("⚠️  Downgrade not implemented for SQLite")
        print("   For PostgreSQL, use: ALTER TABLE dining_rooms DROP COLUMN is_active")

if __name__ == "__main__":
    print("🔧 Adding is_active to dining rooms...")
    upgrade()