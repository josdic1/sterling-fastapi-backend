# migrations/add_meal_type_to_reservations.py
#!/usr/bin/env python3
"""
Migration: Add meal_type to reservations table (cross-db, idempotent)

- Adds meal_type column if missing
- Backfills existing reservations:
    - lunch if start_time between 11:00 and 13:59
    - otherwise dinner
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from database import engine


def _column_exists(table_name: str, column_name: str) -> bool:
    insp = inspect(engine)
    cols = [c["name"] for c in insp.get_columns(table_name)]
    return column_name in cols


def upgrade():
    with engine.connect() as conn:
        dialect = conn.dialect.name

        # Add column if missing
        if dialect == "postgresql":
            conn.execute(text("""
                ALTER TABLE reservations
                ADD COLUMN IF NOT EXISTS meal_type VARCHAR
            """))
        else:
            if not _column_exists("reservations", "meal_type"):
                conn.execute(text("""
                    ALTER TABLE reservations
                    ADD COLUMN meal_type VARCHAR
                """))

        # Backfill NULL meal_type
        if dialect == "postgresql":
            conn.execute(text("""
                UPDATE reservations
                SET meal_type = CASE
                    WHEN start_time::time >= TIME '11:00:00'
                     AND start_time::time <  TIME '14:00:00'
                    THEN 'lunch'
                    ELSE 'dinner'
                END
                WHERE meal_type IS NULL
            """))
        else:
            # SQLite: start_time is typically stored as "HH:MM"
            conn.execute(text("""
                UPDATE reservations
                SET meal_type = CASE
                    WHEN substr(start_time, 1, 2) BETWEEN '11' AND '13'
                    THEN 'lunch'
                    ELSE 'dinner'
                END
                WHERE meal_type IS NULL
            """))

        conn.commit()

    print("✅ meal_type ensured and backfilled on reservations")


def downgrade():
    with engine.connect() as conn:
        dialect = conn.dialect.name

        if dialect == "postgresql":
            conn.execute(text("""
                ALTER TABLE reservations
                DROP COLUMN IF EXISTS meal_type
            """))
            conn.commit()
            print("✅ meal_type dropped (if it existed)")
            return

        print("⚠️  SQLite downgrade not performed (DROP COLUMN may not be supported).")
        print("   If you really need it, recreate the table without meal_type.")


if __name__ == "__main__":
    upgrade()
