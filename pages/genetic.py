import streamlit as st
import pandas as pd
from services.genetic_test_predictor import train_genetic_model

def show():
    st.header("🧬 Genetic Test Recommendation")
    
    # 1. Load the "Brain"
    clf, encoders, feature_columns = train_genetic_model()

    with st.form("genetic_test_form"):
        age = st.number_input("Age", 1, 120, 30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        parental_history = st.radio("Parental History of Disease", ["Yes", "No"])
        sibling_history = st.radio("Sibling History of Disease", ["Yes", "No"])
        num_relatives = st.number_input("Number of Relatives with Disease", 0, 10, 0)
        known_mutation = st.radio("Known Genetic Mutation in Family", ["Yes", "No"])
        early_onset = st.radio("Early Onset Cases in Family", ["Yes", "No"])
        env_risk = st.selectbox("Environmental Risk Exposure", ["Low", "Moderate", "High"])

        submitted = st.form_submit_button("🔍 Predict Genetic Test Need")
