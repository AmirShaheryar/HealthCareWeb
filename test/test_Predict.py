import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from services import predict as app

@pytest.fixture
def mock_df():
    return pd.DataFrame({
        "fever": [1, 0, 1],
        "cough": [0, 1, 1],
        "fatigue": [1, 1, 0],
        "disease": ["Flu", "Cold", "Flu"]
    })

def test_train_model(mock_df):
    with patch("pandas.read_csv", return_value=mock_df):
        model, symptoms = app.train_model()
        
        assert len(symptoms) == 3
        assert "disease" not in symptoms
        assert hasattr(model, "predict")

def test_prediction_logic(mock_df):
    with patch("pandas.read_csv", return_value=mock_df):
        model, symptoms = app.train_model()
        
        # Simulating user selecting 'fever'
        selected = ["fever"]
        input_vector = [1 if sym in selected else 0 for sym in symptoms]
        
        prediction = model.predict([input_vector])[0]
        probs = model.predict_proba([input_vector])[0]
        
        assert prediction in mock_df["disease"].values
        assert 0 <= max(probs) <= 1

@patch("streamlit.columns")
@patch("streamlit.button")
@patch("streamlit.checkbox")
def test_show_ui_elements(mock_checkbox, mock_button, mock_columns, mock_df):
    with patch("pandas.read_csv", return_value=mock_df):
        # Mocking Streamlit layout to ensure it runs without a browser
        mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_button.return_value = False 
        
        try:
            app.show()
        except Exception as e:
            pytest.fail(f"show() raised an exception: {e}")

def test_vectorization_math():
    ALL_SYMPTOMS = ["headache", "nausea", "chills"]
    selected = ["nausea"]
    
    input_vector = [1 if sym in selected else 0 for sym in ALL_SYMPTOMS]
    
    assert input_vector == [0, 1, 0]
    assert len(input_vector) == len(ALL_SYMPTOMS)

def test_model_confidence_range(mock_df):
    with patch("pandas.read_csv", return_value=mock_df):
        model, _ = app.train_model()
        test_input = [[1, 0, 0]]
        
        conf = max(model.predict_proba(test_input)[0]) * 100
        assert 0 <= conf <= 100