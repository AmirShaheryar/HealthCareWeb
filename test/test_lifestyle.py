import pytest
import numpy as np
from unittest.mock import MagicMock
from services import life_Style_Predictor as app  # Replace with your actual filename

@pytest.fixture(scope="module")
def trained_assets():
    """Fixture to train the model once for the test session."""
    model, scaler = app.train_and_load_model()
    return model, scaler

def test_model_training_output(trained_assets):
    """Verify the model and scaler are initialized correctly."""
    model, scaler = trained_assets
    assert isinstance(scaler, app.StandardScaler)
    assert isinstance(model, app.MultiOutputClassifier)

def test_prediction_output_structure(trained_assets):
    """Test if the prediction returns the expected dictionary structure."""
    model, scaler = trained_assets
    result = app.predict_lifestyle(
        age=25, gender="M", weight=70, height=1.75, 
        activity=2, sleep=5, diet=2, 
        model=model, scaler=scaler
    )
    
    assert "probabilities" in result
    assert "recommendations" in result
    assert len(result["probabilities"]) == 4
    assert isinstance(result["recommendations"], list)

def test_scaling_consistency(trained_assets):
    """Ensure the scaler is actually transforming the input."""
    model, scaler = trained_assets
    
    # Manually scale a known input
    raw_input = np.array([[30, 0, 70, 1.7, 3, 7, 3]])
    scaled_input = scaler.transform(raw_input)
    
    # Check that the scaled values are not identical to raw values (StandardScaler effect)
    assert not np.array_equal(raw_input, scaled_input)

def test_gender_encoding(trained_assets):
    """Verify that 'M' and 'F' are handled without crashing."""
    model, scaler = trained_assets
    
    res_m = app.predict_lifestyle(30, "M", 70, 1.8, 3, 7, 3, model, scaler)
    res_f = app.predict_lifestyle(30, "F", 70, 1.8, 3, 7, 3, model, scaler)
    
    assert res_m is not None
    assert res_f is not None

def test_recommendation_logic():
    """
    Test the recommendation mapping specifically by mocking 
    the model's probability output.
    """
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    
    # Mock predict_proba to return 80% chance for index 0 and 2
    # MultiOutputClassifier returns a list of arrays: [array([[prob_0, prob_1]]), ...]
    mock_model.predict_proba.return_value = [
        np.array([[0.2, 0.8]]), # Sleep: True
        np.array([[0.9, 0.1]]), # Activity: False
        np.array([[0.1, 0.9]]), # Diet: True
        np.array([[0.8, 0.2]])  # Lifestyle: False
    ]
    
    # We don't care about the scaler transform result here
    mock_scaler.transform.return_value = np.zeros((1, 7))

    result = app.predict_lifestyle(20, "M", 60, 1.6, 1, 1, 1, mock_model, mock_scaler)
    
    # Based on our mock probs > 0.5: Index 0 and 2 should be in recommendations
    assert "Improve sleep" in result["recommendations"]
    assert "Adjust diet" in result["recommendations"]
    assert "Increase activity" not in result["recommendations"]

def test_synthetic_data_logic(trained_assets):
    """
    Check if a 'perfect' healthy profile results in 'Maintain lifestyle'.
    Note: Since it's a Random Forest on synthetic data, this is a 
    probabilistic check.
    """
    model, scaler = trained_assets
    # High sleep (8), High activity (5), High diet (4)
    result = app.predict_lifestyle(30, "F", 60, 1.6, 5, 8, 4, model, scaler)
    
    # Index 3 is "Maintain lifestyle"
    # We check if it's among the likely recommendations
    assert result["probabilities"][3] > result["probabilities"][0]