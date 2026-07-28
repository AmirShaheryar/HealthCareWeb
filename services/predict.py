import pandas as pd
import streamlit as st
from sklearn.linear_model import LogisticRegression
import os

DATA_DIR = "data"
DATASET_PATH = os.path.join(DATA_DIR, "disease_dataset.csv")

@st.cache_resource
def train_model():
    if not os.path.exists(DATASET_PATH):
        st.error(f"Dataset not found at {DATASET_PATH}. Please ensure the 'data' folder exists.")
        return None, []
        
    df = pd.read_csv(DATASET_PATH)
    X = df.drop("disease", axis=1)
    y = df["disease"]
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model, list(X.columns)

def show():
    st.title("🩺 Disease Prediction Module")
    
    model, ALL_SYMPTOMS = train_model()
    
    if model is None:
        return

    st.write("Select your symptoms:")
    selected = []
    cols = st.columns(3)
    
    for i, symptom in enumerate(ALL_SYMPTOMS):
        if cols[i % 3].checkbox(symptom.replace('_', ' ').title(), key=symptom):
            selected.append(symptom)
            
    if st.button("Predict Now"):
        if selected:

            input_values = [1 if sym in selected else 0 for sym in ALL_SYMPTOMS]
            
            input_df = pd.DataFrame([input_values], columns=ALL_SYMPTOMS)
            

            prediction = model.predict(input_df)[0]
            conf = max(model.predict_proba(input_df)[0]) * 100
            
            st.success(f"Result: {prediction}")
            st.info(f"Confidence: {round(conf, 2)}%")
        else:
            st.warning("Please select at least one symptom.")