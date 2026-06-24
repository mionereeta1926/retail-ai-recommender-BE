from flask import Blueprint
from connection import get_connection
import random

import os
from dotenv import load_dotenv

load_dotenv()

CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")
BUCKET_NAME = os.getenv("BUCKET_NAME")
ATTACHMENT_URL = f"{CLOUDFRONT_DOMAIN}/"

items_bp = Blueprint("items", __name__)

@items_bp.route("/items", methods=["GET"])
def get_items():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            item_id,
            item_name,
            item_description,
            image_url,
            item_price,
            active

        FROM items

        WHERE active = TRUE

        ORDER BY item_name
        """
    )

    rows = cursor.fetchall()

    conn.close()

    items = []

    for row in rows:

        items.append({

            "item_id": row[0],
            "item_name": row[1],
            "item_description": row[2],
            "image_url": ATTACHMENT_URL + row[3],
            "item_price": row[4],
            "active": row[5]

        })

    return {

        "success": True,
        "data": items

    }

@items_bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            item_id,
            item_name,
            item_description,
            image_url,
            item_price,
            active

        FROM items

        WHERE item_id=%s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    conn.close()

    if item is None:

        return {

            "success": False,
            "message": "Item not found"

        }, 404

    return {

        "success": True,

        "data": {

            "item_id": item[0],
            "item_name": item[1],
            "item_description": item[2],
            "image_url": ATTACHMENT_URL + item[3],
            "item_price": item[4],
            "active": item[5]

        }

    }

@items_bp.route("/recommendations/<int:item_id>", methods=["GET"])
def recommendations(item_id):

    conn = get_connection()
    cursor = conn.cursor()

    # ======================================================
    # Get collaborative filtering recommendations ONLY
    # ======================================================
    cursor.execute("""
        SELECT
            ir.recommended_item_id,
            ir.score,
            i.item_name,
            i.item_description,
            i.image_url,
            i.item_price
        FROM item_recommendations ir
        JOIN items i
            ON i.item_id = ir.recommended_item_id
        WHERE ir.item_id = %s
          AND i.active = TRUE
          AND ir.score >= 50
        ORDER BY ir.score DESC
        LIMIT 8
    """, (item_id,))

    rows = cursor.fetchall()

    recommendations_list = []

    for row in rows:

        recommendations_list.append({
            "item_id": row[0],
            "item_name": row[2],
            "item_description": row[3],
            "image_url": ATTACHMENT_URL + row[4],
            "item_price": row[5],
            "score": round(float(row[1]), 2)
        })

    conn.close()

    return {
        "success": True,
        "recommendations": recommendations_list
    }