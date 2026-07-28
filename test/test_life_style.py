import pytest
import numpy as np
from unittest.mock import MagicMock
from services import life_Style_Predictor as app 

@pytest.fixture(scope="module")
def trained_assets():
    model, scaler = app.train_and_load_model()
    return model, scaler

def test_model_initialization(trained_assets):
    model, scaler = trained_assets
    assert isinstance(scaler, app.StandardScaler)
    assert isinstance(model, app.MultiOutputClassifier)

def test_predict_structure(trained_assets):
    model, scaler = trained_assets
    result = app.predict_lifestyle(30, "M", 70, 1.75, 3, 7, 3, model, scaler)
    
    assert "probabilities" in result
    assert "recommendations" in result
    assert len(result["probabilities"]) == 4

def test_gender_normalization(trained_assets):
    model, scaler = trained_assets
    res_lower = app.predict_lifestyle(25, "m", 70, 1.7, 3, 7, 3, model, scaler)
    res_upper = app.predict_lifestyle(25, "M", 70, 1.7, 3, 7, 3, model, scaler)
    assert res_lower["probabilities"] == res_upper["probabilities"]

def test_recommendation_mapping():
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    
    mock_model.predict_proba.return_value = [
        np.array([[0.1, 0.9]]), # Index 0: Improve sleep
        np.array([[0.8, 0.2]]), # Index 1: Low prob
        np.array([[0.2, 0.8]]), # Index 2: Adjust diet
        np.array([[0.9, 0.1]])  # Index 3: Low prob
    ]
    mock_scaler.transform.return_value = np.zeros((1, 7))

    result = app.predict_lifestyle(20, "F", 60, 1.6, 1, 1, 1, mock_model, mock_scaler)
    
    assert "Improve sleep" in result["recommendations"]
    assert "Adjust diet" in result["recommendations"]
    assert "Increase activity" not in result["recommendations"]

def test_scaling_effect(trained_assets):
    model, scaler = trained_assets
    raw_input = np.array([[40, 1, 80, 1.8, 2, 6, 2]])
    scaled_input = scaler.transform(raw_input)
    assert not np.array_equal(raw_input, scaled_input)

@pytest.mark.parametrize("age,weight,height", [
    (18, 45, 1.5),
    (70, 100, 2.0),
])
def test_boundary_inputs(trained_assets, age, weight, height):
    model, scaler = trained_assets
    result = app.predict_lifestyle(age, "F", weight, height, 1, 4, 1, model, scaler)
    assert result is not None