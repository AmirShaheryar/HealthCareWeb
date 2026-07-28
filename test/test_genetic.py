import pandas as pd
import pytest
from services.genetic_test_predictor import train_genetic_model


def fake_data():
    return pd.DataFrame({
        "Patient ID": [1,2,3,4,5,6,7,8],
        "Gender": ["M","F","M","F","M","F","M","F"],
        "Parental History": ["Yes","No","Yes","No","Yes","No","Yes","No"],
        "Sibling History": ["Yes","No","No","Yes","No","Yes","No","Yes"],
        "Known Genetic Mutation": ["Yes","No","Yes","No","Yes","No","Yes","No"],
        "Early Onset Cases in Family": ["Yes","No","Yes","No","Yes","No","Yes","No"],
        "Environmental Risk Exposure": ["High","Low","Medium","Low","High","Low","Medium","Low"],
        "geneticTest": ["Positive","Negative","Positive","Negative","Positive","Negative","Positive","Negative"]
    })


# 🔹 MOCK pandas.read_csv
def test_model_training(monkeypatch):

    def mock_read_csv(*args, **kwargs):
        return fake_data()

    monkeypatch.setattr(pd, "read_csv", mock_read_csv)

    model, encoders, cols = train_genetic_model()

    # ✅ Assertions
    assert model is not None
    assert isinstance(encoders, dict)
    assert len(cols) > 0