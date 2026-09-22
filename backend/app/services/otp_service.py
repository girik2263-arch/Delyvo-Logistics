import hashlib
import secrets
from datetime import datetime, timedelta, timezone


OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
MAX_ATTEMPTS = 5


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp):
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def otp_expiry():
    return (
        datetime.now(timezone.utc)
        + timedelta(minutes=OTP_EXPIRY_MINUTES)
    ).isoformat()


def is_expired(expires_at):
    expiry = datetime.fromisoformat(expires_at)

    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc) >= expiry


def verify_otp_hash(stored_hash, otp):
    return secrets.compare_digest(
        stored_hash,
        hash_otp(otp)
    )
