import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def upgrade():
    """Add meal_type column to reservations table"""
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("PRAGMA table_info(reservations)"))
        columns = [row[1] for row in result]
        
        if 'meal_type' not in columns:
            # Add column
            conn.execute(text("""
                ALTER TABLE reservations 
                ADD COLUMN meal_type VARCHAR
            """))
            print("✅ Added meal_type column")
        else:
            print("ℹ️  meal_type column already exists")
        
        # Set default values for existing records that don't have meal_type set
        conn.execute(text("""
            UPDATE reservations 
            SET meal_type = CASE 
                WHEN CAST(start_time AS TIME) >= '11:00:00' 
                     AND CAST(start_time AS TIME) < '14:00:00' 
                THEN 'lunch'
                ELSE 'dinner'
            END
            WHERE meal_type IS NULL
        """))
        
        conn.commit()
    print("✅ Migration complete")

if __name__ == "__main__":
    upgrade()