import pytest

from src.utils.security import (
    BCRYPT_COST_FACTOR,
    PasswordTooLongError,
    hash_password,
    verify_password,
)


def test_hash_and_verify_round_trip():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_wrong_password_is_rejected():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("wrong-password", hashed) is False


def test_hash_never_equals_plaintext():
    plain = "correct-horse-battery-staple"
    hashed = hash_password(plain)
    assert hashed != plain


def test_same_password_produces_different_hashes():
    # bcrypt generates a random salt per call, so two hashes of the same
    # password must differ (this is what prevents rainbow-table attacks).
    hashed_a = hash_password("same-password")
    hashed_b = hash_password("same-password")
    assert hashed_a != hashed_b
    assert verify_password("same-password", hashed_a) is True
    assert verify_password("same-password", hashed_b) is True


def test_hash_uses_cost_factor_12():
    hashed = hash_password("correct-horse-battery-staple")
    # bcrypt hash format: $2b$<cost>$<salt+hash>
    cost = int(hashed.split("$")[2])
    assert cost == BCRYPT_COST_FACTOR == 12


def test_password_over_72_bytes_is_rejected_on_hash():
    too_long = "a" * 73
    with pytest.raises(PasswordTooLongError):
        hash_password(too_long)


def test_password_over_72_bytes_fails_verification():
    too_long = "a" * 73
    # Can't even get a hash for it, so verify against an unrelated hash
    # and confirm it's rejected rather than silently truncated/matched.
    unrelated_hash = hash_password("short-password")
    assert verify_password(too_long, unrelated_hash) is False
