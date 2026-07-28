
import pytest

from services import report_Pdf as rp


def test_clean_text_normalizes():
    out = rp.clean_text("  HELLO,  World\n")
    assert out.strip() == "hello world"
    assert "  " not in out.strip()


@pytest.mark.parametrize(
    "snippet, expected_key, expected_val",
    [
        ("hemoglobin: 11.2", "hemoglobin", 11.2),
        ("hgb - 14", "hemoglobin", 14.0),
        ("wbc: 7.5", "wbc", 7.5),
        ("platelets 250", "platelets", 250.0),
        ("blood sugar 140", "glucose", 140.0),
        ("hba1c: 7.0", "hba1c", 7.0),
        ("total cholesterol: 210", "cholesterol", 210.0),
        ("ldl: 140", "ldl", 140.0),
        ("hdl 35", "hdl", 35.0),
        ("triglycerides 180", "triglycerides", 180.0),
        ("creatinine 1.5", "creatinine", 1.5),
    ],
)
def test_extract_values_patterns(snippet, expected_key, expected_val):
    data = rp.extract_values(snippet)
    assert data.get(expected_key) == pytest.approx(expected_val)


def test_analyze_values_low_hb_and_high_glucose():
    findings = rp.analyze_values({"hemoglobin": 10.0, "glucose": 200.0})
    joined = " ".join(findings).lower()
    assert "haemoglobin" in joined or "hemoglobin" in joined
    assert "glucose" in joined


def test_analyze_values_empty_defaults():
    findings = rp.analyze_values({})
    assert any("no major abnormal" in f.lower() for f in findings)


def test_generate_recommendations_from_extracted():
    advice = rp.generate_recommendations({"hemoglobin": 11.0, "glucose": 130.0})
    assert any("iron" in a.lower() for a in advice)


def test_process_report_end_to_end():
    text = "Patient labs: hemoglobin: 12.0 glucose: 130 hba1c 6.0"
    out = rp.process_report(text)
    assert "extracted" in out and "findings" in out and "advice" in out
    assert isinstance(out["extracted"], dict)
