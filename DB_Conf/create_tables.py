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

# =====================================================
# CONNECT
# =====================================================

try:

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    conn.autocommit = True

    cursor = conn.cursor()

    print("Connected to PostgreSQL")

    # =====================================================
    # CUSTOMER TABLE
    # =====================================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS customers (

        user_id SERIAL PRIMARY KEY,

        username VARCHAR(100) NOT NULL,

        email VARCHAR(255) UNIQUE NOT NULL,

        password VARCHAR(255) NOT NULL,

        phone_number VARCHAR(30),

        active BOOLEAN DEFAULT TRUE

    );

    """)

    print("customers created")

    # =====================================================
    # ITEMS TABLE
    # =====================================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS items (

        item_id SERIAL PRIMARY KEY,

        item_name VARCHAR(255) NOT NULL,

        item_description TEXT,
                   
        image_url VARCHAR(255),
                   
        item_price DECIMAL(12,2) DEFAULT 0,

        active BOOLEAN DEFAULT TRUE

    );

    """)

    print("items created")

    # =====================================================
    # INVOICE TABLE
    # =====================================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS invoices (

        invoice_id SERIAL PRIMARY KEY,

        invoice_date DATE NOT NULL,

        amount DECIMAL(12,2) DEFAULT 0,

        user_id INTEGER NOT NULL,

        payment VARCHAR(100),

        active BOOLEAN DEFAULT TRUE,

        CONSTRAINT fk_customer

            FOREIGN KEY(user_id)

            REFERENCES customers(user_id)

            ON DELETE CASCADE

    );

    """)

    print("invoices created")

    # =====================================================
    # INVOICE ITEMS TABLE
    # =====================================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS invoice_items (

        id SERIAL PRIMARY KEY,

        invoice_id INTEGER NOT NULL,

        item_id INTEGER NOT NULL,

        CONSTRAINT fk_invoice

            FOREIGN KEY(invoice_id)

            REFERENCES invoices(invoice_id)

            ON DELETE CASCADE,

        CONSTRAINT fk_item

            FOREIGN KEY(item_id)

            REFERENCES items(item_id)

            ON DELETE CASCADE,

        CONSTRAINT unique_invoice_item

            UNIQUE(invoice_id, item_id)

    );

    """)

    print("invoice_items created")

    print("\n===================================")
    print("Database created successfully.")
    print("===================================")

except Exception as e:

    print("Error:")
    print(e)

finally:

    try:
        cursor.close()
        conn.close()
    except:
        pass