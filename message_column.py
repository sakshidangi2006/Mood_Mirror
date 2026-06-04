from db import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE journal_entries
        ADD COLUMN message TEXT;
    """))

    conn.commit()

print("message column added")