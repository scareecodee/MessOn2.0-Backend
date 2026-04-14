import os
import json
import firebase_admin
from firebase_admin import credentials, auth

firebase_config = os.getenv("FIREBASE_CONFIG")

if firebase_config:
    cred = credentials.Certificate(json.loads(firebase_config))
    firebase_admin.initialize_app(cred)
else:
    print("Firebase config not found")


def verify_firebase_token(id_token: str):
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        print("Firebase token verification failed:", str(e))
        return None

    return None

