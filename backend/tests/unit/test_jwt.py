import time

import pytest

from src.utils.jwt import (
    InvalidTokenError,
    TokenExpiredError,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


def test_access_token_round_trip():
    token = create_access_token("user-123")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_refresh_token_round_trip():
    token = create_refresh_token("user-123")
    payload = decode_refresh_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "refresh"


def test_access_token_rejected_as_refresh_token():
    token = create_access_token("user-123")
    with pytest.raises(InvalidTokenError):
        decode_refresh_token(token)


def test_refresh_token_rejected_as_access_token():
    token = create_refresh_token("user-123")
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_tampered_token_is_rejected():
    token = create_access_token("user-123")
    # Flip a character inside the payload segment (not the very last
    # character of the signature: base64url's last symbol only carries 2
    # significant bits for a 32-byte HMAC digest, so some flips there
    # decode to the exact same signature bytes and wouldn't prove anything).
    header, payload, signature = token.split(".")
    tampered_payload = payload[:-1] + ("A" if payload[-1] != "A" else "B")
    tampered = f"{header}.{tampered_payload}.{signature}"
    with pytest.raises(InvalidTokenError):
        decode_access_token(tampered)


def test_garbage_token_is_rejected():
    with pytest.raises(InvalidTokenError):
        decode_access_token("not-a-jwt-at-all")


def test_expired_access_token_is_rejected(monkeypatch):
    import src.utils.jwt as jwt_module

    monkeypatch.setattr(
        jwt_module.get_jwt_settings(),
        "access_token_expire_minutes",
        0,
    )
    token = create_access_token("user-123")
    time.sleep(1.1)
    with pytest.raises(TokenExpiredError):
        decode_access_token(token)


def test_extra_claims_are_included():
    token = create_access_token("user-123", extra_claims={"email": "a@example.com"})
    payload = decode_access_token(token)
    assert payload["email"] == "a@example.com"
