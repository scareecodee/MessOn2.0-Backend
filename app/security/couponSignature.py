import hmac
import hashlib
import base64


SECRET_KEY = b"SUPER_SECRET_KEY_CHANGE_THIS"


def sign_payload(data: str) -> str:
    signature = hmac.new(
        SECRET_KEY,
        data.encode(),
        hashlib.sha256
    ).digest()

    return base64.urlsafe_b64encode(signature).decode()
