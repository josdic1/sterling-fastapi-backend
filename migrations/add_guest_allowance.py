# migrations/add_guest_allowance.py
#!/usr/bin/env python3
"""
Migration: Add guest_allowance to members table (cross-db, idempotent)

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
                ALTER TABLE members
                ADD COLUMN IF NOT EXISTS guest_allowance INTEGER NOT NULL DEFAULT 4
            """))
        else:
            # SQLite + anything else: check first, then add
            if not _column_exists("members", "guest_allowance"):
                conn.execute(text("""
                    ALTER TABLE members
                    ADD COLUMN guest_allowance INTEGER NOT NULL DEFAULT 4
                """))

        # Backfill if anything ends up NULL
        conn.execute(text("""
            UPDATE members
            SET guest_allowance = 4
            WHERE guest_allowance IS NULL
        """))

        conn.commit()

    print("✅ guest_allowance ensured on members")


def downgrade():
    with engine.connect() as conn:
        dialect = conn.dialect.name

        if dialect == "postgresql":
            conn.execute(text("""
                ALTER TABLE members
                DROP COLUMN IF EXISTS guest_allowance
            """))
            conn.commit()
            print("✅ guest_allowance dropped (if it existed)")
            return

        # SQLite: DROP COLUMN support depends on version; avoid risky auto-drop.
        print("⚠️  SQLite downgrade not performed (DROP COLUMN may not be supported).")
        print("   If you really need it, recreate the table without guest_allowance.")


if __name__ == "__main__":
    upgrade()
