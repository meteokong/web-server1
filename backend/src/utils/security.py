"""Password hashing utilities (bcrypt, cost factor 12 per research.md)."""

import bcrypt

BCRYPT_COST_FACTOR = 12

# bcrypt truncates/ignores input past 72 bytes; reject longer passwords
# up front rather than silently hashing only a prefix of them.
_MAX_PASSWORD_BYTES = 72


class PasswordTooLongError(ValueError):
    """Raised when a password exceeds bcrypt's 72-byte input limit."""


def hash_password(plain_password: str) -> str:
    """Hash ``plain_password`` with bcrypt, returning a string safe to store."""
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > _MAX_PASSWORD_BYTES:
        raise PasswordTooLongError(
            f"password must be at most {_MAX_PASSWORD_BYTES} bytes when UTF-8 encoded"
        )
    salt = bcrypt.gensalt(rounds=BCRYPT_COST_FACTOR)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True if ``plain_password`` matches ``password_hash``."""
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > _MAX_PASSWORD_BYTES:
        return False
    return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))
