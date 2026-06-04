from sqlalchemy import text
from db import engine

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE journal_entries ADD COLUMN text TEXT NOT NULL DEFAULT ''"))
    conn.commit()
print("Done")