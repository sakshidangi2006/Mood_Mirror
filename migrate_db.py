from db import engine
from sqlalchemy import text

with engine.connect() as conn:

    try:
        conn.execute(text("""
            ALTER TABLE journal_entries
            ADD COLUMN insights TEXT;
        """))
        print("Added insights column")
    except Exception as e:
        print("Insights column may already exist:", e)

    try:
        conn.execute(text("""
            ALTER TABLE journal_entries
            ADD COLUMN recommendations TEXT;
        """))
        print("Added recommendations column")
    except Exception as e:
        print("Recommendations column may already exist:", e)

    conn.commit()

print("Migration completed")