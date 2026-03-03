import os
import firebase_admin
from firebase_admin import credentials, auth

# get absolute path to app/ directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# build absolute path to the json file
SERVICE_ACCOUNT_PATH = os.path.join(
    BASE_DIR,
    "security",
    "firebase_service_account.json"
)

# initialize firebase admin only once

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)


def verify_firebase_token(id_token: str):
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        print("Firebase token verification failed:", str(e))
        return None

    return None

