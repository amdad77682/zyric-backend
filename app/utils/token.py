import secrets
from datetime import datetime, timedelta


def generate_reset_token() -> str:
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)


def is_token_expired(expires_at: datetime) -> bool:
    """Check if a token has expired"""
    return datetime.utcnow() > expires_at


def get_token_expiry(hours: int = 24) -> datetime:
    """Get expiry datetime for a token (default 24 hours)"""
    return datetime.utcnow() + timedelta(hours=hours)
