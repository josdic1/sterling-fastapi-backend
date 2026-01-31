import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def upgrade():
    """Add guest_allowance column to members table"""
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE members 
            ADD COLUMN guest_allowance INTEGER DEFAULT 4 NOT NULL
        """))
        conn.commit()
    print("✅ Added guest_allowance column to members")

def downgrade():
    """Remove guest_allowance column"""
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE members 
            DROP COLUMN guest_allowance
        """))
        conn.commit()
    print("✅ Removed guest_allowance column")

if __name__ == "__main__":
    upgrade()