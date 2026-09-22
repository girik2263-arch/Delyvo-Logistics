import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash, check_password_hash


SESSION_DAYS = 7


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def create_token():
    return secrets.token_urlsafe(48)


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_expiry():
    return (
        datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    ).isoformat()
