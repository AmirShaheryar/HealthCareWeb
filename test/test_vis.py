
import pandas as pd

from services import vis


def test_get_ml_prediction_insufficient_rows():
    df = pd.DataFrame({"steps": [1, 2], "sleep": [7, 6], "stress": [3, 4], "med_cost": [100, 200]})
    assert vis.get_ml_prediction(df, steps=5000, sleep=7, stress=5) is None


def test_get_ml_prediction_returns_non_negative_int():
    df = pd.DataFrame(
        {
            "steps": [3000, 6000, 9000],
            "sleep": [6, 7, 8],
            "stress": [2, 4, 6],
            "med_cost": [500, 400, 300],
        }
    )
    pred = vis.get_ml_prediction(df, steps=8000, sleep=7, stress=3)
    assert isinstance(pred, int)
    assert pred >= 0


def test_calculate_health_risk_range():
    r = vis.calculate_health_risk(steps=10000, sleep=7, stress=0)
    assert 0 <= r <= 1


def test_get_dynamic_costs_scales_with_risk():
    base = vis.get_dynamic_costs(0)
    high = vis.get_dynamic_costs(0.5)
    assert high["Diabetes"] > base["Diabetes"]


def test_get_comparison_chart_returns_figure():
    fig, risk = vis.get_comparison_chart(prevention_annual=10000, steps=8000, sleep=7, stress=3)
    assert fig is not None
    assert isinstance(risk, float)


def test_generate_ai_insight_branches():
    assert "stress" in vis.generate_ai_insight(8000, 7, 9).lower()
    assert "activity" in vis.generate_ai_insight(4000, 7, 3).lower()
    assert "sleep" in vis.generate_ai_insight(8000, 5, 3).lower()
    assert "balanced" in vis.generate_ai_insight(9000, 8, 3).lower()


def test_get_pakistan_insights_returns_figure():
    fig = vis.get_pakistan_insights(user_steps=12000, user_stress=4)
    assert fig is not None
