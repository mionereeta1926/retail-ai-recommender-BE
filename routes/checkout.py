from flask import Blueprint, request
from itertools import combinations
from datetime import datetime


from connection import get_connection
from datetime import datetime

checkout_bp = Blueprint("checkout", __name__)

@checkout_bp.route("/checkout", methods=["POST"])
def checkout():

    data = request.json

    user_id = data.get("user_id")
    items = data.get("items")
    payment = data.get("payment")

    if user_id is None:
        return {"success": False, "message": "User ID is required"}, 400

    if not items:
        return {"success": False, "message": "Please select at least one item"}, 400

    if not payment:
        return {"success": False, "message": "Payment method is required"}, 400

    conn = get_connection()
    cursor = conn.cursor()

    # ======================================================
    # Check user
    # ======================================================
    cursor.execute("""
        SELECT user_id
        FROM customers
        WHERE user_id=%s AND active=TRUE
    """, (user_id,))

    if cursor.fetchone() is None:
        conn.close()
        return {"success": False, "message": "User not found"}, 404

    # ======================================================
    # Validate items
    # ======================================================
    valid_items = []
    total_amount = 0

    for item_id in items:

        cursor.execute("""
            SELECT item_id, item_price
            FROM items
            WHERE item_id=%s AND active=TRUE
        """, (item_id,))

        item = cursor.fetchone()

        if item:
            valid_items.append(item[0])
            total_amount += float(item[1])

    if not valid_items:
        conn.close()
        return {"success": False, "message": "No valid items"}, 400

    amount = total_amount

    # ======================================================
    # Create invoice
    # ======================================================
    cursor.execute("""
        INSERT INTO invoices
        (invoice_date, amount, user_id, payment, active)
        VALUES (%s,%s,%s,%s,%s)
        RETURNING invoice_id
    """, (
        datetime.now(),
        amount,
        user_id,
        payment,
        True
    ))

    invoice_id = cursor.fetchone()[0]

    # ======================================================
    # Insert invoice items
    # ======================================================
    for item_id in valid_items:
        cursor.execute("""
            INSERT INTO invoice_items
            (invoice_id, item_id)
            VALUES (%s,%s)
        """, (invoice_id, item_id))

    # ======================================================
    # RECOMMENDER UPDATE (FIXED)
    # ======================================================

    pairs = list(combinations(valid_items, 2))

    for a, b in pairs:

        # ---------------------------------------------
        # Step 1: update co-occurrence (A → B)
        # ---------------------------------------------
        cursor.execute("""
            INSERT INTO item_recommendations
            (item_id, recommended_item_id, co_occurrence_count, created_datetime, updated_datetime)
            VALUES (%s,%s,1,%s,%s)
            ON CONFLICT (item_id, recommended_item_id)
            DO UPDATE SET
                co_occurrence_count = item_recommendations.co_occurrence_count + 1,
                updated_datetime = EXCLUDED.updated_datetime
        """, (a, b, datetime.now(), datetime.now()))

        # ---------------------------------------------
        # Step 2: update co-occurrence (B → A)
        # ---------------------------------------------
        cursor.execute("""
            INSERT INTO item_recommendations
            (item_id, recommended_item_id, co_occurrence_count, created_datetime, updated_datetime)
            VALUES (%s,%s,1,%s,%s)
            ON CONFLICT (item_id, recommended_item_id)
            DO UPDATE SET
                co_occurrence_count = item_recommendations.co_occurrence_count + 1,
                updated_datetime = EXCLUDED.updated_datetime
        """, (b, a, datetime.now(), datetime.now()))

        # ---------------------------------------------
        # Step 3: compute TRUE CF score
        # score = co_occurrence(A,B) / total_occurrence(A)
        # ---------------------------------------------

        cursor.execute("""
            SELECT COUNT(DISTINCT invoice_id)
            FROM invoice_items
            WHERE item_id = %s
        """, (a,))

        total_a = cursor.fetchone()[0] or 1

        cursor.execute("""
            SELECT co_occurrence_count
            FROM item_recommendations
            WHERE item_id=%s AND recommended_item_id=%s
        """, (a, b))

        co_ab = cursor.fetchone()[0]

        score_ab = (co_ab / total_a) * 100

        cursor.execute("""
            UPDATE item_recommendations
            SET score=%s
            WHERE item_id=%s AND recommended_item_id=%s
        """, (score_ab, a, b))

        # ---------------------------------------------
        # Step 4: symmetric B → A
        # ---------------------------------------------

        cursor.execute("""
            SELECT COUNT(DISTINCT invoice_id)
            FROM invoice_items
            WHERE item_id = %s
        """, (b,))

        total_b = cursor.fetchone()[0] or 1

        cursor.execute("""
            SELECT co_occurrence_count
            FROM item_recommendations
            WHERE item_id=%s AND recommended_item_id=%s
        """, (b, a))

        co_ba = cursor.fetchone()[0]

        score_ba = (co_ba / total_b) * 100

        cursor.execute("""
            UPDATE item_recommendations
            SET score=%s
            WHERE item_id=%s AND recommended_item_id=%s
        """, (score_ba, b, a))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Checkout successful",
        "invoice": {
            "invoice_id": invoice_id,
            "total_items": len(valid_items),
            "amount": amount,
            "payment": payment
        }
    }