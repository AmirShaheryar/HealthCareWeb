
import pytest

from modules.AQI import (
    generate_health_warning,
    get_age_multiplier,
)
from modules.db import DEMO_USERS
from modules import auth as _auth
from services import nutrition_service as _svc


def test_aqi_generate_health_warning():
    result = generate_health_warning(
        100, "PM10", ["None / Unknown"], "Adult (18\u201360)", ["None"], "Light walk"
    )
    assert "risk_score" in result
    assert result["aqi"] == 100


def test_age_multiplier_en_dash_adult():
    assert get_age_multiplier("Adult (18\u201360)") == 1.0


def test_demo_users_constant():
    assert "patient@demo.com" in DEMO_USERS


def test_nutrition_service_iron_condition():
    condition = "Iron Deficiency / Anaemia"
    ranked = _svc.rank_budget_foods(condition)
    assert len(ranked) >= 1
    assert _svc.calculate_savings(condition) >= 0


def test_security_auth_functions():
    assert _auth.is_valid_email("user@example.com") is True
    score, label, _, tips = _auth.password_strength("Aa1!aaaa")
    assert score >= 4 and label == "Strong"
    h = _auth.hash_password("Secret1!")
    assert _auth.check_password("Secret1!", h) is True
