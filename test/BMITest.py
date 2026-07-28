import pytest
from services.BMI import get_bmi_details, get_recommendations

@pytest.mark.parametrize("weight, height, expected_label, expected_icon", [
    (50, 1.75, "Underweight", "🔵"),
    (70, 1.75, "Healthy Weight", "🟢"),
    (85, 1.75, "Overweight", "🟡"),
    (110, 1.75, "Obese", "🔴"),
])
def test_get_bmi_details_categories(weight, height, expected_label, expected_icon):
    bmi, label, icon = get_bmi_details(weight, height)
    
    # Check if the label and icon match the expected output
    assert label == expected_label
    assert icon == expected_icon
    # Check if the math is correct (BMI = weight / height^2)
    assert bmi == pytest.approx(weight / (height ** 2), rel=1e-2)

# --- 2. Testing Recommendation Logic ---
def test_get_recommendations_all_bad():
    """Test when all inputs are below threshold"""
    results = get_recommendations(sleep=4, activity=2, diet=2)
    
    # Should have 3 recommendations
    assert len(results) == 3
    # Check for specific icons to ensure the right branches were hit
    icons = [r["icon"] for r in results]
    assert "😴" in icons
    assert "🏃‍♂️" in icons
    assert "🥗" in icons

def test_get_recommendations_perfect_score():
    """Test the 'Maintain' branch when all scores are high"""
    results = get_recommendations(sleep=8, activity=5, diet=4)
    
    assert len(results) == 1
    assert results[0]["icon"] == "🌟"
    assert "excellent" in results[0]["text"]

@pytest.mark.parametrize("sleep, activity, diet, expected_count", [
    (8, 2, 4, 1), # Only activity is low
    (5, 5, 2, 2), # Sleep and diet are low
])
def test_recommendation_counts(sleep, activity, diet, expected_count):
    results = get_recommendations(sleep, activity, diet)
    assert len(results) == expected_count