import pytest

from services.nlp_utils import detect_risk


@pytest.mark.parametrize(
    "text, expected",
    [
        ("patient has chest pain", "🔴 Critical"),
        ("heart attack symptoms", "🔴 Critical"),
        ("high fever and chills", "🟠 High"),
        ("vomiting since morning", "🟠 High"),
        ("mild cough and fatigue", "🟡 Medium"),
        ("everything feels fine today", "🟢 Low"),
    ],
)
def test_detect_risk_levels(text, expected):
    assert detect_risk(text) == expected


def test_detect_risk_critical_order_prefers_critical_over_high():
    """Critical keywords are checked before high-risk ones."""
    assert detect_risk("chest pain and high fever") == "🔴 Critical"