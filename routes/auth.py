from flask import Blueprint, request, session, jsonify, make_response
from datetime import datetime, timedelta

import bcrypt

from connection import get_connection
from helpers.validator import validate_signup
from helpers.validator import validate_login
from helpers.email_helper import send_verification_email
from helpers.email_helper import send_reset_password
from helpers.key_handler import generate_policy

# Sign policy
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64

import os
from dotenv import load_dotenv

load_dotenv()

CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")
KEY_PAIR_ID = os.getenv("KEY_PAIR_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
BUCKET_NAME = os.getenv("BUCKET_NAME")
RESOURCE_URL = f"{CLOUDFRONT_DOMAIN}/{BUCKET_NAME}/*"



auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():

    data = request.json

    errors = validate_signup(data)

    if len(errors) > 0:

        return {
            "success": False,
            "errors": errors
        }, 400

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM customers
        WHERE email=%s
        """,
        (data["email"],)
    )

    user = cursor.fetchone()

    if user:

        conn.close()

        return {
            "success": False,
            "message": "Email already exists"
        }, 400

    password = bcrypt.hashpw(
        data["password"].encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute(
        """
        INSERT INTO customers
        (
            username,
            email,
            password,
            phone_number,
            active
        )

        VALUES
        (
            %s,%s,%s,%s,%s
        )
        """,

        (
            data["username"],
            data["email"],
            password,
            data["phone_number"],
            False
        )
    )

    conn.commit()

    conn.close()

    verification = send_verification_email(
        data["email"]
    )

    return {

        "success": True,
        "message": "Signup successful",

        "verification_code":

        verification["verification_code"]

    }

@auth_bp.route("/verify-email", methods=["POST"])
def verify():

    data = request.json

    if data["code"] != "123456":

        return {

            "success": False,

            "message": "Invalid verification code"

        }, 400

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        UPDATE customers

        SET active=True

        WHERE email=%s

        """,

        (

            data["email"],

        )

    )

    conn.commit()

    conn.close()

    return {

        "success": True,

        "message": "Email verified"

    }

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json
    errors = validate_login(data)

    if len(errors) > 0:
        return {"success": False, "errors": errors}, 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE email=%s
    """, (data["email"],))

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return {"success": False, "message": "User not found"}, 404

    if not user[5]:
        return {"success": False, "message": "Please verify email"}, 400

    password_ok = bcrypt.checkpw(
        data["password"].encode(),
        user[3].encode()
    )

    if not password_ok:
        return {"success": False, "message": "Wrong password"}, 400

    # -----------------------------
    # SESSION (your app auth)
    # -----------------------------
    session["user_id"] = user[0]

    # -----------------------------
    # CLOUDFRONT SIGNED COOKIES
    # -----------------------------
    expiry = datetime.utcnow() + timedelta(hours=1)

    policy = generate_policy(expiry)

    # Load private key
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = f.read()


    signature = base64.b64encode(
        serialization.load_pem_private_key(
            private_key,
            password=None
        ).sign(
            policy.encode(),
            padding.PKCS1v15(),
            hashes.SHA1()
        )
    ).decode()

    policy_encoded = base64.b64encode(policy.encode()).decode()

    # -----------------------------
    # RESPONSE WITH COOKIES
    # -----------------------------
    response = make_response(jsonify({
        "success": True,
        "message": "Login successful",
        "user_id": user[0]
    }))

    response.set_cookie(
    "CloudFront-Policy",
    policy_encoded,
    httponly=True,
    secure=True,
    samesite="None",
    domain=".cloudfront.net"
    )

    response.set_cookie(
        "CloudFront-Signature",
        signature,
        httponly=True,
        samesite="None",
        secure=True
    )

    response.set_cookie(
        "CloudFront-Key-Pair-Id",
        KEY_PAIR_ID,
        httponly=True,
        samesite="None",
        secure=True
    )

    return response

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():

    data = request.json

    result = send_reset_password(

        data["email"]

    )

    return {

        "success": True,

        "reset_code":

        result["reset_code"]

    }