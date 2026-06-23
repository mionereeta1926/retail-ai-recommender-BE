from flask import Blueprint
from flask import request

import bcrypt

from connection import get_connection

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            user_id,
            username,
            email,
            phone_number,
            active
        FROM customers
        WHERE user_id=%s
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:

        return {
            "success": False,
            "message": "User not found"
        }, 404

    return {
        "success": True,
        "data": {
            "user_id": user[0],
            "username": user[1],
            "email": user[2],
            "phone_number": user[3],
            "active": user[4]
        }
    }

@profile_bp.route("/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):

    data = request.json

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE customers

        SET
            username=%s,
            phone_number=%s

        WHERE user_id=%s
        """,

        (
            data["username"],
            data["phone_number"],
            user_id
        )
    )

    conn.commit()

    conn.close()

    return {
        "success": True,
        "message": "Profile updated"
    }

@profile_bp.route("/reset-password/<int:user_id>", methods=["PUT"])
def reset_password(user_id):

    data = request.json

    password = bcrypt.hashpw(
        data["password"].encode(),
        bcrypt.gensalt()
    ).decode()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE customers

        SET password=%s

        WHERE user_id=%s
        """,

        (
            password,
            user_id
        )
    )

    conn.commit()

    conn.close()

    return {
        "success": True,
        "message": "Password updated"
    }

@profile_bp.route("/invoices/<int:user_id>", methods=["GET"])
def invoices(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            invoice_id,
            invoice_date,
            amount,
            payment,
            active

        FROM invoices

        WHERE user_id=%s

        ORDER BY invoice_date DESC
        """,

        (
            user_id,
        )
    )

    rows = cursor.fetchall()

    conn.close()

    invoice_list = []

    for row in rows:

        invoice_list.append({

            "invoice_id": row[0],
            "invoice_date": row[1],
            "amount": float(row[2]),
            "payment": row[3],
            "active": row[4]

        })

    return {

        "success": True,

        "data": invoice_list

    }

@profile_bp.route("/logout", methods=["POST"])
def logout():

    return {

        "success": True,

        "message": "Logout successful"

    }