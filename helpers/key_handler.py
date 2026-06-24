import os
from dotenv import load_dotenv
import json
# Sign policy
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from datetime import datetime, timedelta


load_dotenv()

CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")
KEY_PAIR_ID = os.getenv("KEY_PAIR_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
BUCKET_NAME = os.getenv("BUCKET_NAME")
RESOURCE_URL = f"{CLOUDFRONT_DOMAIN}/*"

def generate_policy(expiry_time):
    policy = {
        "Statement": [{
            "Resource": RESOURCE_URL,
            "Condition": {
                "DateLessThan": {
                    "AWS:EpochTime": int(expiry_time.timestamp())
                }
            }
        }]
    }

    return json.dumps(policy, separators=(",", ":"))

def sign_policy(policy, private_key_bytes):
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=None
        )
    signature = private_key.sign(
        policy.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA1()
    )

    return base64.b64encode(signature).decode("utf-8")

def generate_signed_url(file_path, cf_signer, expiry_minutes=60):
    url = f"{CLOUDFRONT_DOMAIN}/{file_path}"

    expire_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    signed_url = cf_signer.generate_presigned_url(
        url,
        date_less_than=expire_time
    )

    return signed_url

