import psycopg2
import os
from dotenv import load_dotenv

# =====================================================
# DATABASE CONFIGURATION
# =====================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def main():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
    )

    try:
        # We'll use autocommit OFF, so CREATE TABLE is committed at the end.
        conn.autocommit = False

        with conn.cursor() as cur:
            print(f"Connected to database: {DB_NAME}")

            # Create table explicitly in public schema
            create_sql = """
CREATE TABLE IF NOT EXISTS public.item_recommendations (
    recommendation_id BIGSERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    recommended_item_id INT NOT NULL,
    co_occurrence_count INT NOT NULL DEFAULT 0,
    score DECIMAL(10,5) NOT NULL DEFAULT 0,
    created_datetime TIMESTAMP NOT NULL,
    updated_datetime TIMESTAMP NOT NULL,
    UNIQUE (item_id, recommended_item_id)
);
"""

            cur.execute(create_sql)
            conn.commit()
            print("CREATE TABLE executed and committed.")

            # Verify existence
            cur.execute("""
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'item_recommendations';
            """)
            exists = cur.fetchone() is not None

            print("Verified exists in public.item_recommendations:", exists)

            if not exists:
                raise RuntimeError("Table not found after CREATE. Check schema/db/permissions.")

    except Exception as e:
        # This will show the real error if CREATE TABLE failed.
        print("ERROR:", repr(e))
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()