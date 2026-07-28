"""Tests for ``modules.auth`` password and validation helpers."""

import pytest

from modules import auth


def test_is_valid_email_accepts_and_rejects():
    # Regex allows one domain label before the TLD (subdomains like a.b.co.uk are not matched).
    assert auth.is_valid_email("user.name+tag@example.com") is True
    assert auth.is_valid_email("not-an-email") is False
    assert auth.is_valid_email("") is False


def test_password_strength_progression():
    s0, label0, _, tips0 = auth.password_strength("short")
    assert s0 == 0 and label0 == "Weak" and tips0

    s1, label1, _, _ = auth.password_strength("abcdefgh")
    assert s1 == 1 and label1 == "Weak"

    s3, label3, _, _ = auth.password_strength("Abcdefgh1")
    assert s3 == 3 and label3 == "Good"

    s4, label4, color4, _ = auth.password_strength("Abcdefgh1!")
    assert s4 == 4 and label4 == "Strong"
    assert color4.startswith("#")


def test_hash_and_check_password_round_trip():
    h = auth.hash_password("SecretPass1!")
    assert h.startswith("$2")
    assert auth.check_password("SecretPass1!", h) is True
    assert auth.check_password("Wrong", h) is False


def test_check_password_plain_fallback():
    assert auth.check_password("demo", "demo") is True
    assert auth.check_password("x", "demo") is False
