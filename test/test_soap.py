import pytest

from services.soap_service import generate_soap


def test_soap_output():
    text = "Patient has fever and cough"
    result = generate_soap(text)

    assert "S — Subjective" in result
    assert "O — Objective" in result
    assert "A — Assessment" in result
    assert "P — Plan" in result


def test_soap_lists_symptoms_when_present():
    out = generate_soap("Fever, cough, and fatigue reported")
    assert "Fever" in out
    assert "Cough" in out
    assert "Fatigue" in out


def test_soap_general_illness_when_no_symptom_keywords():
    out = generate_soap("I want a routine checkup")
    assert "General illness" in out


@pytest.mark.parametrize("text", ["", "   "])
def test_soap_handles_minimal_text(text):
    out = generate_soap(text or " ")
    assert "S — Subjective" in out