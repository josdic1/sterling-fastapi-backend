# migrations/add_is_active_to_dining_rooms.py
#!/usr/bin/env python3
"""
Migration: Add is_active to dining_rooms table (cross-db, idempotent)

- Postgres: uses ADD COLUMN IF NOT EXISTS
- SQLite: checks schema via SQLAlchemy inspector before ALTER TABLE
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

        if dialect == "postgresql":
            conn.execute(text("""
                ALTER TABLE dining_rooms
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE
            """))
        else:
            if not _column_exists("dining_rooms", "is_active"):
                # SQLite stores booleans as ints usually
                conn.execute(text("""
                    ALTER TABLE dining_rooms
                    ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1
                """))

        # Backfill anything that might be NULL
        if dialect == "postgresql":
            conn.execute(text("""
                UPDATE dining_rooms
                SET is_active = TRUE
                WHERE is_active IS NULL
            """))
        else:
            conn.execute(text("""
                UPDATE dining_rooms
                SET is_active = 1
                WHERE is_active IS NULL
            """))

        conn.commit()

    print("✅ is_active ensured on dining_rooms")


def downgrade():
    with engine.connect() as conn:
        dialect = conn.dialect.name

        if dialect == "postgresql":
            conn.execute(text("""
                ALTER TABLE dining_rooms
                DROP COLUMN IF EXISTS is_active
            """))
            conn.commit()
            print("✅ is_active dropped (if it existed)")
            return

        print("⚠️  SQLite downgrade not performed (DROP COLUMN may not be supported).")
        print("   If you really need it, recreate the table without is_active.")


if __name__ == "__main__":
    upgrade()
