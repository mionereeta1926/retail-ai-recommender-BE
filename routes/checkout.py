from flask import Blueprint
from flask import request

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

        return {
            "success": False,
            "message": "User ID is required"
        }, 400

    if items is None or len(items) == 0:

        return {
            "success": False,
            "message": "Please select at least one item"
        }, 400

    if payment is None or payment == "":

        return {
            "success": False,
            "message": "Payment method is required"
        }, 400

    conn = get_connection()
    cursor = conn.cursor()

    # Check user exists

    cursor.execute(
        """
        SELECT user_id

        FROM customers

        WHERE user_id=%s
        AND active=TRUE
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        conn.close()

        return {
            "success": False,
            "message": "User not found"
        }, 404

    # Validate every item

    valid_items = []
    total_amount = 0

    for item_id in items:

        cursor.execute(
            """
            SELECT
                item_id,
                price

            FROM items

            WHERE item_id=%s
            AND active=TRUE
            """,
            (item_id,)
        )

        item = cursor.fetchone()

        if item:

            valid_items.append(item[0])

            total_amount += float(item[1])
            
    amount = total_amount
    # Create invoice

    cursor.execute(
        """
        INSERT INTO invoices
        (
            invoice_date,
            amount,
            user_id,
            payment,
            active
        )

        VALUES
        (
            %s,%s,%s,%s,%s
        )

        RETURNING invoice_id
        """,

        (
            datetime.now(),
            amount,
            user_id,
            payment,
            True
        )
    )

    invoice_id = cursor.fetchone()[0]

    # Create invoice items

    for item_id in valid_items:

        cursor.execute(
            """
            INSERT INTO invoice_items
            (
                invoice_id,
                item_id
            )

            VALUES
            (
                %s,%s
            )
            """,

            (
                invoice_id,
                item_id
            )
        )

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