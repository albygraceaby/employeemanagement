"""Small, dependency-free JWT implementation for TalentSphere API authentication."""
import base64
import hashlib
import hmac
import json
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache


ALGORITHM = "HS256"
ACCESS_LIFETIME = 15 * 60
REFRESH_LIFETIME = 7 * 24 * 60 * 60


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _sign(message: str) -> str:
    digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), message.encode("ascii"), hashlib.sha256
    ).digest()
    return _b64(digest)


def issue_token(user, token_type="access"):
    now = int(time.time())
    lifetime = ACCESS_LIFETIME if token_type == "access" else REFRESH_LIFETIME
    payload = {
        "sub": str(user.pk),
        "type": token_type,
        "iat": now,
        "exp": now + lifetime,
    }
    header = {"alg": ALGORITHM, "typ": "JWT"}
    encoded_header = _b64(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _b64(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_payload}"
    return f"{signing_input}.{_sign(signing_input)}"


def decode_token(token, expected_type="access"):
    try:
        header_b64, payload_b64, signature = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}"
        if not hmac.compare_digest(signature, _sign(signing_input)):
            return None
        header = json.loads(_unb64(header_b64))
        payload = json.loads(_unb64(payload_b64))
        if header.get("alg") != ALGORITHM or header.get("typ") != "JWT":
            return None
        if payload.get("type") != expected_type or int(payload.get("exp", 0)) <= int(time.time()):
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None

        cache_key = f"jwt_user_cache:{user_id}"
        user = cache.get(cache_key)
        if user is None:
            User = get_user_model()
            user = User.objects.filter(pk=user_id, is_active=True).first()
            if user:
                cache.set(cache_key, user, timeout=60)
        return user
    except (ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeDecodeError):
        return None
