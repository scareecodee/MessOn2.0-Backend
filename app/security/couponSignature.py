from datetime import datetime
import hmac
import hashlib
import base64
from app.core.config import get_settings

settings=get_settings()


SECRET_KEY = settings.coupon_secret_key.encode()


def sign_payload(data: str) -> str:
    signature = hmac.new(
        SECRET_KEY,
        data.encode(),
        hashlib.sha256
    ).digest()

    return base64.urlsafe_b64encode(signature).decode()

def verify_payload_signature(payload) -> str : 

    unsigned = f"{payload.coupon_id}|{payload.user_id}|{payload.date}|{payload.meal}|{payload.expires_at}"

    expected_signature = sign_payload(unsigned)
    # return hmac.compare_digest(expected_signature, payload.signature)
    return expected_signature