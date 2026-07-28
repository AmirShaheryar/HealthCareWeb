import pytest

from modules import AQI as aqi


@pytest.mark.parametrize(
    "value, expected_label",
    [
        (0, "Good"),
        (50, "Good"),
        (51, "Moderate"),
        (100, "Moderate"),
        (101, "Unhealthy for Sensitive Groups"),
        (150, "Unhealthy for Sensitive Groups"),
        (151, "Unhealthy"),
        (200, "Unhealthy"),
        (201, "Very Unhealthy"),
        (300, "Very Unhealthy"),
        (301, "Hazardous"),
        (500, "Hazardous"),
    ],
)
def test_get_aqi_category_boundaries(value, expected_label):
    cat = aqi.get_aqi_category(value)
    assert cat["label"] == expected_label
    assert "risk" in cat and isinstance(cat["risk"], int)
    assert 0 <= cat["risk"] <= 5


def test_get_pollutant_multiplier_known_and_default():
    assert aqi.get_pollutant_multiplier("PM2.5") == 1.4
    assert aqi.get_pollutant_multiplier("CO") == 1.0
    assert aqi.get_pollutant_multiplier("Unknown") == 1.0


def test_get_genetic_sensitivity_none_baseline():
    out = aqi.get_genetic_sensitivity(["None / Unknown"])
    assert out["level"] == "Low / baseline genetic sensitivity"
    assert all(v == 1.0 for v in out["weights"].values())


def test_get_genetic_sensitivity_stacked_variants():
    out = aqi.get_genetic_sensitivity(
        ["GSTP1 (oxidative stress sensitivity)", "NQO1 (detoxification deficiency)"]
    )
    assert out["weights"]["PM2.5"] > 1.0
    assert "sensitivity" in out["level"].lower()


def test_get_age_multiplier_and_condition_bonus():
    assert aqi.get_age_multiplier("Child (under 12)") == 1.4
    assert aqi.get_age_multiplier("Adult (18–60)") == 1.0
    assert aqi.get_age_multiplier("Unknown") == 1.0
    assert aqi.get_condition_bonus(["Asthma", "COPD"]) == pytest.approx(3.3)
    assert aqi.get_condition_bonus(["None"]) == 0.0


def test_get_activity_multiplier():
    assert aqi.get_activity_multiplier("Intense exercise") == 2.2
    assert aqi.get_activity_multiplier("No outdoor activity") == 1.0


def test_compute_personal_risk_score_clamped():
    score = aqi.compute_personal_risk_score(
        aqi=500,
        pollutant="PM2.5",
        genetic_data=aqi.get_genetic_sensitivity(
            ["GSTP1 (oxidative stress sensitivity)", "NQO1 (detoxification deficiency)", "ACE (cardiovascular sensitivity)"]
        ),
        age_group="Child (under 12)",
        conditions=["Asthma", "COPD", "Heart disease"],
        activity="Intense exercise",
    )
    assert score <= 10.0


def test_classify_personal_risk_buckets():
    assert aqi.classify_personal_risk(1.0)["level"] == "Low risk"
    assert aqi.classify_personal_risk(2.0)["level"] == "Moderate risk"
    assert aqi.classify_personal_risk(5.0)["level"] == "High risk"
    assert aqi.classify_personal_risk(8.0)["level"] == "Critical risk"


def test_get_symptoms_to_watch_merges_conditions():
    symptoms = aqi.get_symptoms_to_watch("PM2.5", ["Asthma", "Heart disease"])
    assert "Coughing / throat irritation" in symptoms
    assert "Asthma attack / wheezing episode" in symptoms
    assert "Chest pressure" in symptoms


def test_get_action_recommendations_high_score():
    actions = aqi.get_action_recommendations(
        score=7.0, aqi=160, activity="Intense exercise", conditions=["Asthma"], age_group="Child (under 12)"
    )
    texts = " ".join(a["text"] for a in actions)
    assert "indoors" in texts.lower() or "mask" in texts.lower()


def test_generate_health_warning_structure():
    report = aqi.generate_health_warning(
        aqi=120,
        pollutant="PM10",
        genetic_variants=["None / Unknown"],
        age_group="Adult (18–60)",
        conditions=["None"],
        activity="Light walk",
    )
    for key in ("aqi", "pollutant", "aqi_category", "genetic_data", "risk_score", "personal_risk", "symptoms", "actions"):
        assert key in report
    assert isinstance(report["symptoms"], list)
    assert isinstance(report["actions"], list)
