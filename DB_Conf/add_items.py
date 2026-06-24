import psycopg2

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

items = [
    ("Chair", "Chair", "YWO6W9PE8A.jpg", 30.00, True),
    ("Laptop", "Laptop", "GEGJ50CT2A.jpg", 3000.00, True),
    ("Mouse", "Mouse", "OH12THCAD0.jpg", 25.00, True),
    ("Projector", "Projector", "VK65LPMEN1.jpg", 50.00, True),
    ("Speaker", "Speaker", "98FN3NNA5H.jpg", 100.00, True),
    ("Table", "Table", "VNNV9ZIM5M.jpg", 120.00, True),
    ("TV", "TV", "YKIZFPS17A.jpg", 1500.00, True),
    ("Whiteboard", "Whiteboard", "ABPWCXA9Q3.jpg", 30.00, True),
]

insert_sql = """
INSERT INTO items (item_name, item_description, image_url, item_price, active)
VALUES (%s, %s, %s, %s, %s)
"""

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
                for name, description, image_url, price, active in items:
                    cur.execute(
                        insert_sql,
                        (name, description, image_url, float(price), active),
                    )

        print("Items inserted successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()