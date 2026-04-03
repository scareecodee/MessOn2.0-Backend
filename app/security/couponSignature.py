from datetime import datetime
import hmac
import hashlib
import base64
from app.core.config import get_settings
from app.utils.unsignedCouponPayload import build_unsigned_from_payload

settings=get_settings()


SECRET_KEY = settings.coupon_secret_key.encode()


def sign_payload(data: str) -> str:
    signature = hmac.new(
        SECRET_KEY,
        data.encode(),
        hashlib.sha256
    ).digest()

    return  base64.urlsafe_b64encode(signature).decode()

def verify_payload_signature(payload):
    unsigned = build_unsigned_from_payload(payload)
    expected_signature = sign_payload(unsigned)
    #
    # print("expected_signature", expected_signature)
    # print("payload signature",payload.signature)

    return hmac.compare_digest(expected_signature, payload.signature)