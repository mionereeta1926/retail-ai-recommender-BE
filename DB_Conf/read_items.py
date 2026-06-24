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
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT item_id, item_name, item_description, image_url, item_price, active
                    FROM items
                    ORDER BY item_id;
                """)
                rows = cur.fetchall()

        for r in rows:
            item_id, item_name, item_description, image_url, item_price, active = r
            print(
                f"[{item_id}] {item_name} | {item_description} | "
                f"{image_url} | price={item_price} | active={active}"
            )

    finally:
        conn.close()

if __name__ == "__main__":
    main()