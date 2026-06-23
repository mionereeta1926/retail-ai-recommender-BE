import os
from dotenv import load_dotenv
import json

load_dotenv()

CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")
KEY_PAIR_ID = os.getenv("KEY_PAIR_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
BUCKET_NAME = os.getenv("BUCKET_NAME")
RESOURCE_URL = f"{CLOUDFRONT_DOMAIN}/{BUCKET_NAME}/*"

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